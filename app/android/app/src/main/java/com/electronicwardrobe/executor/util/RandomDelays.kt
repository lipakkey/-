package com.electronicwardrobe.executor.util

import kotlinx.coroutines.delay
import kotlin.random.Random

data class DelayConfig(
    val microMinMs: Long = 800,
    val microMaxMs: Long = 1500,
    val browseMinMs: Long = 3000,
    val browseMaxMs: Long = 6000,
    val macroMinMs: Long = 10 * 60 * 1000L,
    val macroMaxMs: Long = 20 * 60 * 1000L,
)

class RandomDelays(
    private val config: DelayConfig = DelayConfig(),
    private val random: Random = Random.Default,
) {
    suspend fun microDelay() {
        delay(pick(config.microMinMs, config.microMaxMs))
    }

    suspend fun randomBrowseDelay() {
        delay(pick(config.browseMinMs, config.browseMaxMs))
    }

    suspend fun macroDelay() {
        delay(pick(config.macroMinMs, config.macroMaxMs))
    }

    private fun pick(min: Long, max: Long): Long {
        if (max <= min) return min
        return random.nextLong(min, max)
    }
}
