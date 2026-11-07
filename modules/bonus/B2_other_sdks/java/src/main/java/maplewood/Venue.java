package maplewood;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import org.a2aproject.sdk.server.PublicAgentCard;
import org.a2aproject.sdk.server.agentexecution.AgentExecutor;
import org.a2aproject.sdk.server.agentexecution.RequestContext;
import org.a2aproject.sdk.server.tasks.AgentEmitter;
import org.a2aproject.sdk.spec.*;

/** A native Java executor: shared inventory, integer cents, no model or purchases. */
@ApplicationScoped
public class Venue {
    @Produces @PublicAgentCard
    public AgentCard card() {
        return AgentCard.builder().name("Granite Hall Venues (Java)")
            .description("Quote the cheapest available room with sufficient capacity.")
            .version("1.0.0")
            .supportedInterfaces(List.of(new AgentInterface("JSONRPC", "http://127.0.0.1:8401")))
            .capabilities(AgentCapabilities.builder().streaming(true).pushNotifications(false).build())
            .defaultInputModes(List.of("application/json"))
            .defaultOutputModes(List.of("application/json"))
            .securitySchemes(Map.of("bearer", HTTPAuthSecurityScheme.builder().scheme("bearer").build()))
            .securityRequirements(List.of(new SecurityRequirement(Map.of("bearer", List.of()))))
            .skills(List.of(AgentSkill.builder().id("venues.quote").name("Venue quote")
                .description("Accept guests and date; return an unsigned, nonbinding quote in cents.")
                .tags(List.of("venues", "quote")).build())).build();
    }

    @Produces
    public AgentExecutor executor() {
        return new AgentExecutor() {
            public void execute(RequestContext context, AgentEmitter emitter) {
                if (context.getTask() == null) emitter.submit();
                emitter.startWork();
                try {
                    Map<?, ?> brief = context.getMessage().parts().stream()
                        .filter(p -> p instanceof DataPart).map(p -> ((DataPart)p).data())
                        .filter(p -> p instanceof Map).map(p -> (Map<?, ?>)p)
                        .findFirst().orElseThrow();
                    Object count = brief.containsKey("guests") ? brief.get("guests") : 40;
                    if (!(count instanceof Number n) || !Double.isFinite(n.doubleValue())
                        || n.doubleValue() != n.intValue() || n.intValue() < 1 || n.intValue() > 1000)
                        throw new IllegalArgumentException("Invalid guest count");
                    int guests = ((Number)count).intValue();
                    String date = brief.containsKey("date") ? brief.get("date").toString() : "2027-06-01";
                    JsonArray rooms = JsonParser.parseString(Files.readString(
                        Path.of(System.getenv("MAPLEWOOD_VENUES_FILE")))).getAsJsonArray();
                    JsonObject selected = rooms.asList().stream().map(r -> r.getAsJsonObject())
                        .filter(r -> r.get("capacity").getAsInt() >= guests)
                        .filter(r -> r.getAsJsonObject("availability").has(date)
                            && r.getAsJsonObject("availability").get(date).getAsBoolean())
                        .min(Comparator.comparingInt(r -> r.get("price_cents").getAsInt())).orElseThrow();
                    // KEY IDEA: the SDK owns task state and serialization across languages.
                    emitter.addArtifact(List.of(new DataPart(Map.of(
                        "vendor", "venues", "selection", selected.get("id").getAsString(),
                        "currency", "USD", "total_cents", selected.get("price_cents").getAsInt(),
                        "guests", guests, "approved", false))), "quote", "quote", null);
                    emitter.complete();
                } catch (IllegalArgumentException | java.util.NoSuchElementException e) {
                    emitter.reject();
                } catch (java.io.IOException e) {
                    emitter.fail();
                }
            }
            public void cancel(RequestContext context, AgentEmitter emitter) {
                throw new TaskNotCancelableError();
            }
        };
    }
}
