package com.example.myapplication

import kotlinx.parcelize.Parcelize

@Parcelize
data class Route(
    val transports: List<TransportationItem>
) : Transportation() {
    override fun getAllTransports(): List<TransportationItem> = transports
}
