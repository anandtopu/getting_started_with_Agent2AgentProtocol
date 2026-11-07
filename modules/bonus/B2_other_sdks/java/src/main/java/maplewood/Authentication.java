package maplewood;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import jakarta.enterprise.context.ApplicationScoped;
import io.quarkus.vertx.web.RouteFilter;
import io.vertx.ext.web.RoutingContext;
import org.eclipse.microprofile.config.inject.ConfigProperty;

/** Protect the Vert.x router used by the SDK, before any protocol operation. */
@ApplicationScoped
public class Authentication {
    @ConfigProperty(name = "maplewood.token")
    String token;

    @RouteFilter(100)
    void authenticate(RoutingContext context) {
        if (context.request().method().name().equals("GET")
            && context.normalizedPath().equals("/.well-known/agent-card.json")) {
            context.next();
            return;
        }
        String header = context.request().getHeader("Authorization");
        if (header == null || token.isBlank() || !MessageDigest.isEqual(
            ("Bearer " + token).getBytes(StandardCharsets.UTF_8),
            header.getBytes(StandardCharsets.UTF_8))) {
            context.response().setStatusCode(401).putHeader("WWW-Authenticate", "Bearer").end();
            return;
        }
        context.setUser(io.vertx.ext.auth.User.create(
            new io.vertx.core.json.JsonObject().put("sub", "maplewood:concierge")));
        context.next();
    }
}
