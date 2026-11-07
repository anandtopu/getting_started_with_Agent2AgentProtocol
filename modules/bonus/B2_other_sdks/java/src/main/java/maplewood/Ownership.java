package maplewood;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import jakarta.enterprise.context.ApplicationScoped;
import org.a2aproject.sdk.server.ServerCallContext;
import org.a2aproject.sdk.server.auth.TaskAuthorizationProvider;
import org.a2aproject.sdk.server.auth.TaskOperation;

/** Fail closed for unknown tasks; ownership has the same lifetime as the task store. */
@ApplicationScoped
public class Ownership implements TaskAuthorizationProvider {
    private final ConcurrentMap<String, String> owners = new ConcurrentHashMap<>();

    public boolean checkCreate(ServerCallContext context, TaskOperation operation) {
        return context.getUser() != null && context.getUser().isAuthenticated();
    }
    public void recordOwnership(ServerCallContext context, String id, TaskOperation operation) {
        if (checkCreate(context, operation)) owners.putIfAbsent(id, context.getUser().getUsername());
    }
    public boolean isTaskRecorded(String id) {
        return owners.containsKey(id);
    }
    public boolean checkRead(ServerCallContext context, String id, TaskOperation operation) {
        if (operation == TaskOperation.LIST_TASKS && id.isEmpty()) return checkCreate(context, operation);
        return checkCreate(context, operation) && context.getUser().getUsername().equals(owners.get(id));
    }
    public boolean checkWrite(ServerCallContext context, String id, TaskOperation operation) {
        return checkRead(context, id, operation);
    }
}
