package com.example.whatsapp_recovery

import android.content.Intent
import android.os.Build
import android.provider.Settings
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : FlutterActivity() {
	private val CHANNEL = "com.example.whatsapp_recovery/notifications"

	override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
		super.configureFlutterEngine(flutterEngine)

		MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
			when (call.method) {
				"openNotificationAccess" -> {
					val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
					if (intent.resolveActivity(packageManager) != null) {
						startActivity(intent)
						result.success(true)
					} else {
						result.error("UNAVAILABLE", "Cannot open notification access settings", null)
					}
				}
				"getMessages" -> {
					CoroutineScope(Dispatchers.Main).launch {
						val data = withContext(Dispatchers.IO) {
							AppDatabase.getInstance(this@MainActivity).messageDao().getAll()
								.map { m ->
									mapOf(
										"id" to m.id,
										"sender" to m.sender,
										"content" to m.content,
										"packageName" to m.packageName,
										"timestamp" to m.timestamp,
										"isDeleted" to m.isDeleted
									)
								}
						}
						result.success(data)
					}
				}
				else -> result.notImplemented()
			}
		}
	}
}

