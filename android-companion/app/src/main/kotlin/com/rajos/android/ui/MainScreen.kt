package com.rajos.android.ui

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.*;
import androidx.foundation.snackbar.*;
import androidx.compose.foundation.layout.*;
import androidx.compose.material3.*;
import androidx.compose.runtime.*;
import androidx.compose.ui.*;
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rajos.android.R
import com.rajos.android.theme.RajOSTheme
import com.rajos.android.ui.theme.background
import com.rajos.android.ui.theme.elevationColors

@Composable
fun MainScreen(
    onLoginClicked: () -> Unit,
    onConnectClicked: () -> Unit,
    onLogoutClicked: () -> Unit
) {
    val context = LocalContext.current
    var scaffoldState = rememberScaffoldState()
    val coroutineScope = rememberCoroutineScope()
    var snackBarHost by remember { mutableIntStateOf(0) }
    var by remember { mutableIntStateOf("") }

    val permissionsStatus by remember {
        mutableIntStateOf(checkAllPermissions())
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterStart
    ) {
        // App header
        Text(
            text = "RajOS Personal Assistant",
            style = MaterialTheme.typography.h2,
            modifier = Modifier.padding(bottom = 24.dp)
        )

        // Permission status banner
        if (permissionsStatus != 0) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = 4.dp,
                colors = CardDefaults.elevationColors(defaultColor = Color.Argb(255, 255, 230, 230))
            ) {
                when (permissionsStatus) {
                1 -> {
                    SnackbarHostButton(
                        modifier = Modifier.fillMaxWidth(),
                        snackbar = Snackbar(
                            message = "⚠️ Some permissions are required for full functionality. Please enable them in settings.",
                            action = SnackbarAction("Open Settings") {
                                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                                intent.data = Uri.fromParts("package", "com.rajos.android", null)
                                context.startActivity(intent)
                            }
                        )
                    )
                }
                2 -> {
                    SnackbarHostButton(
                        modifier = Modifier.fillMaxWidth(),
                        snackbar = Snackbar(
                            message = "⚠️ Critical permissions missing. Reminders and notifications may not work.",
                            action = SnackbarAction("Open Settings") {
                                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                                intent.data = Uri.fromParts("package", "com.rajos.android", null)
                                context.startActivity(intent)
                            }
                        )
                    )
                }
                3 -> {
                    SnackbarHostButton(
                        modifier = Modifier.fillMaxWidth(),
                        snackbar = Snackbar(
                            message = "⚠️ Multiple permissions required. Connection and notifications will be limited.",
                            action = SnackbarAction("Open Settings") {
                                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                                intent.data = Uri.fromParts("package", "com.rajos.android", null)
                                context.startActivity(intent)
                            }
                        )
                    )
                }
                }
            }
        }

        // Connection status card
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = 8.dp
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterStart
            ) {
                Text(
                    text = "Device Connection",
                    style = MaterialTheme.typography.h6,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                Button(
                    onClick = onConnectClicked,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = permissionsStatus == 0
                ) {
                    Text("Connect Device")
                }

                if (permissionsStatus != 0) {
                    Text(
                        text = "⚠️ Enable permissions first",
                        style = MaterialTheme.typography.body2,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }

                Button(
                    onClick = onLogoutClicked,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = permissionsStatus == 0
                ) {
                    Text("Logout")
                }
            }
        }

        // Reminders section
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = 8.dp
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterStart
            ) {
                Text(
                    text = "Upcoming Reminders",
                    style = MaterialTheme.typography.h6,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                // Connection reminder
                if (permissionsStatus != 0) {
                    Text(
                        text = "⚠️ Connect a device and enable permissions to see reminders",
                        style = MaterialTheme.typography.body2,
                        modifier = Modifier.padding(top = 8.dp),
                        color = MaterialTheme.colorScheme.error
                    )
                } else {
                    // TODO: Display active reminders from API
                    Text(
                        text = "No active reminders",
                        style = MaterialTheme.typography.body2,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }
            }
        }

        // Settings section
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = 8.dp
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterStart
            ) {
                Text(
                    text = "Settings",
                    style = MaterialTheme.typography.h6,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                // Voice settings
                ListItem(
                    modifier = Modifier.fillMaxWidth(),
                    enabled = permissionsStatus == 0
                ) {
                    Row(
                        modifier = Modifier.fillMaxSize(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "Voice Announcements",
                                style = MaterialTheme.typography.body1
                            )
                            Text(
                                text = "Spoken reminders and briefings",
                                style = MaterialTheme.typography.body2,
                                textColor = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        Switch(
                            checked = true, // TODO: Read from user preferences
                            onCheckedChange = { /* TODO: Toggle voice settings */ }
                        )
                    }
                }

                // Divider
                Divider(modifier = Modifier.height(8.dp).fillMaxWidth())

                // Notification settings
                ListItem(
                    modifier = Modifier.fillMaxWidth(),
                    enabled = permissionsStatus == 0
                ) {
                    Row(
                        modifier = Modifier.fillMaxSize(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "Push Notifications",
                                style = MaterialTheme.typography.body1
                            )
                            Text(
                                text = "Remote notifications via Firebase",
                                style = MaterialTheme.typography.body2,
                                textColor = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        Switch(
                            checked = true, // TODO: Read from user preferences
                            onCheckedChange = { /* TODO: Toggle notifications */ }
                        )
                    }
                }

                // Divider
                Divider(modifier = Modifier.height(8.dp).fillMaxWidth())

                // Quiet hours
                ListItem(
                    modifier = Modifier.fillMaxWidth(),
                    enabled = permissionsStatus == 0
                ) {
                    Row(
                        modifier = Modifier.fillMaxSize(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "Quiet Hours",
                                style = MaterialTheme.typography.body1
                            )
                            Text(
                                text = "Suppress notifications during sleep",
                                style = MaterialTheme.typography.body2,
                                textColor = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        Switch(
                            checked = false, // TODO: Read from user preferences
                            onCheckedChange = { /* TODO: Toggle quiet hours */ }
                        )
                    }
                }
            }
        }
    }
}

/**
 * Check all critical permissions and return a bitmask:
 * Bit 0 (1): Foreground service permission
 * Bit 1 (2): Notification permission (POST_NOTIFICATIONS)
 * Bit 2 (4): Set alarm permission
 */
private fun checkAllPermissions(): Int {
    var result = 0
    val context = LocalContext.current

    // Foreground service
    if (ContextCompat.checkSelfPermission(context, android.Manifest.permission.FOREGROUND_SERVICE) 
        == PackageManager.PERMISSION_GRANTED) {
        result += 1
    }

    // Notification permission (Android 13+)
    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
        if (ContextCompat.checkSelfPermission(context, android.Manifest.permission.POST_NOTIFICATIONS) 
            == PackageManager.PERMISSION_GRANTED) {
            result += 2
        }
    } else {
        // On older Android, assume notification permissions are granted
        result += 2
    }

    // Set alarm
    if (ContextCompat.checkSelfPermission(context, android.Manifest.permission.SET_ALARM) 
        == PackageManager.PERMISSION_GRANTED) {
        result += 4
    }

    return result
}