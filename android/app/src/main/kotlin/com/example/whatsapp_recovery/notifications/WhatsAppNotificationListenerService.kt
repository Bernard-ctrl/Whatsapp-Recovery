package com.example.whatsapp_recovery.notifications

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.text.TextUtils
import android.util.Log
import com.example.whatsapp_recovery.AppDatabase
import com.example.whatsapp_recovery.data.MessageEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class WhatsAppNotificationListenerService : NotificationListenerService() {

    private val scope = CoroutineScope(Dispatchers.IO)
    private val whatsappPackage = "com.whatsapp"
    private val TAG = "WAListener"

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        try {
            if (sbn.packageName != whatsappPackage) return

            val extras = sbn.notification.extras
            val title = extras.getCharSequence("android.title")?.toString()
            val text = extras.getCharSequence("android.text")?.toString()
            val conversationTitle = extras.getCharSequence("android.conversationTitle")?.toString()
            val convoId = when {
                !conversationTitle.isNullOrBlank() -> conversationTitle
                !sbn.tag.isNullOrBlank() -> sbn.tag
                else -> title
            }

            if (TextUtils.isEmpty(title) && TextUtils.isEmpty(text)) return

            // WhatsApp sometimes uses InboxStyle / MessagingStyle; this is MVP simple parse
            val message = MessageEntity(
                sender = title,
                content = text,
                packageName = sbn.packageName,
                timestamp = System.currentTimeMillis(),
                isDeleted = false,
                conversationId = convoId
            )
            scope.launch {
                AppDatabase.getInstance(applicationContext).messageDao().insert(message)
            }
        } catch (e: Exception) {
            Log.e(TAG, "onNotificationPosted error", e)
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification) {
        // Detect deletion message via notification text pattern ("This message was deleted")
        try {
            if (sbn.packageName != whatsappPackage) return
            val extras = sbn.notification.extras
            val text = extras.getCharSequence("android.text")?.toString() ?: return
            if (text.contains("This message was deleted", ignoreCase = true)) {
                // Mark the latest message in this conversation as deleted
                scope.launch {
                    val dao = AppDatabase.getInstance(applicationContext).messageDao()
                    val list = dao.getAll()
                    val latestForConv = list.firstOrNull { it.conversationId == sbn.tag }
                    latestForConv?.let {
                        dao.update(it.copy(isDeleted = true))
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "onNotificationRemoved error", e)
        }
    }
}
