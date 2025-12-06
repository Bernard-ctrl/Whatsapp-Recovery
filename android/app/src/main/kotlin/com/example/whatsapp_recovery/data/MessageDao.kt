package com.example.whatsapp_recovery.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update

@Dao
interface MessageDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insert(message: MessageEntity): Long

    @Update
    fun update(message: MessageEntity)

    @Query("SELECT * FROM messages ORDER BY timestamp DESC")
    fun getAll(): List<MessageEntity>

    @Query("UPDATE messages SET isDeleted = 1 WHERE id = :id")
    fun markDeleted(id: Long)

    @Query("DELETE FROM messages")
    fun deleteAll()
}
