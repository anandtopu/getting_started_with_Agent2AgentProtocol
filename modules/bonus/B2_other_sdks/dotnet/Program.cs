// Official .NET SDK preview lab: native A2A tasks and a deterministic venue quote.
using A2A;
using A2A.AspNetCore;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

var token = Environment.GetEnvironmentVariable("MAPLEWOOD_TOKEN");
if (string.IsNullOrWhiteSpace(token)) throw new InvalidOperationException("MAPLEWOOD_TOKEN is required.");
var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://127.0.0.1:8402");
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 1_000_000);
var card = new AgentCard
{
    Name = "Granite Hall Venues (.NET preview)",
    Description = "Quote available venue capacity. No booking or purchase.",
    Version = "1.0.0",
    SupportedInterfaces = [new AgentInterface {
        Url = "http://127.0.0.1:8402/rpc", ProtocolBinding = "JSONRPC", ProtocolVersion = "1.0" }],
    DefaultInputModes = ["application/json"], DefaultOutputModes = ["application/json"],
    Capabilities = new AgentCapabilities { Streaming = true },
    SecuritySchemes = new() { ["bearer"] = new SecurityScheme {
        HttpAuthSecurityScheme = new HttpAuthSecurityScheme { Scheme = "bearer" } } },
    SecurityRequirements = [new SecurityRequirement { Schemes = new() { ["bearer"] = new StringList() } }],
    Skills = [new AgentSkill { Id = "venues.quote", Name = "Venue quote",
        Description = "Accept guests and date; return the lowest available price in cents.",
        Tags = ["venues", "quote"] }]
};
builder.Services.AddA2AAgent<Venue>(card);
var app = builder.Build();
app.Use(async (context, next) =>
{
    if (context.Request.Method == "GET" && context.Request.Path == "/.well-known/agent-card.json")
    {
        await next(context);
        return;
    }
    var supplied = context.Request.Headers.Authorization.ToString();
    if (!CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes("Bearer " + token),
                                                Encoding.UTF8.GetBytes(supplied)))
    {
        context.Response.StatusCode = 401;
        context.Response.Headers.WWWAuthenticate = "Bearer";
        return;
    }
    await next(context);
});
app.MapA2A("/rpc");
app.MapWellKnownAgentCard(card);
app.Run();

public sealed class Venue : IAgentHandler
{
    public async Task ExecuteAsync(RequestContext context, AgentEventQueue events, CancellationToken cancellation)
    {
        var updater = new TaskUpdater(events, context.TaskId, context.ContextId);
        if (context.Task is null) await updater.SubmitAsync(cancellationToken: cancellation);
        await updater.StartWorkAsync(cancellationToken: cancellation);
        try
        {
            var brief = context.Message.Parts.First(p => p.Data is not null).Data!.Value;
            var count = brief.TryGetProperty("guests", out var value) ? value : JsonSerializer.SerializeToElement(40);
            if (count.ValueKind != JsonValueKind.Number || !count.TryGetDouble(out var number)
                || !double.IsFinite(number) || number != Math.Truncate(number) || number < 1 || number > 1000)
                throw new ArgumentException("Invalid guests");
            int guests = (int)number;
            var date = brief.TryGetProperty("date", out var day) ? day.GetString()! : "2027-06-01";
            using var inventory = JsonDocument.Parse(await File.ReadAllTextAsync(
                Environment.GetEnvironmentVariable("MAPLEWOOD_VENUES_FILE")!, cancellation));
            var selected = inventory.RootElement.EnumerateArray()
                .Where(room => room.GetProperty("capacity").GetInt32() >= guests
                    && room.GetProperty("availability").TryGetProperty(date, out var available)
                    && available.GetBoolean())
                .OrderBy(room => room.GetProperty("price_cents").GetInt32()).First();
            var quote = JsonSerializer.SerializeToElement(new {
                vendor = "venues", selection = selected.GetProperty("id").GetString(),
                currency = "USD", total_cents = selected.GetProperty("price_cents").GetInt32(),
                guests, approved = false });
            // KEY IDEA: SDK events create the same task and artifact contract as Python.
            await updater.AddArtifactAsync([Part.FromData(quote)], artifactId: "quote", name: "quote",
                                           cancellationToken: cancellation);
            await updater.CompleteAsync(cancellationToken: cancellation);
        }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException or KeyNotFoundException)
        {
            await updater.RejectAsync(cancellationToken: cancellation);
        }
        catch (IOException)
        {
            await updater.FailAsync(cancellationToken: cancellation);
        }
    }
}
