package com.aegisgraph.smalab

data class SurfaceEvent(val step: Int, val event: String, val guard: String)

object SurfaceModel {
    private val paths = listOf(
        "parser",
        "link_preview",
        "device_link",
        "media",
        "group_state",
        "pq_migration",
    )

    fun trace(pathId: String, mitigated: Boolean): List<SurfaceEvent> {
        require(pathId in paths) { "unknown path: $pathId" }
        val events = mutableListOf(
            SurfaceEvent(1, "input_received", "none"),
            SurfaceEvent(2, "parsed", if (mitigated) "schema_check" else "none"),
        )
        if (mitigated) {
            events += SurfaceEvent(3, "security_boundary", "${pathId}_boundary")
        }
        events += SurfaceEvent(4, "state_transition", if (mitigated) "capability_boundary" else "none")
        return events
    }
}
