package com.example.whatsapp_recovery.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "messages")
data class MessageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sender: String?,
    val content: String?,
    val packageName: String,
    val timestamp: Long,
    val isDeleted: Boolean = false,
    val conversationId: String? = null
)
