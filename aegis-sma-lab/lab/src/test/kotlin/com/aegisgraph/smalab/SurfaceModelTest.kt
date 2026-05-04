package com.aegisgraph.smalab

import kotlin.test.Test
import kotlin.test.assertTrue

class SurfaceModelTest {
    @Test
    fun mitigatedTraceAddsBoundary() {
        val baseline = SurfaceModel.trace("parser", mitigated = false)
        val mitigated = SurfaceModel.trace("parser", mitigated = true)
        assertTrue(baseline.none { it.event == "security_boundary" })
        assertTrue(mitigated.any { it.event == "security_boundary" })
    }
}
