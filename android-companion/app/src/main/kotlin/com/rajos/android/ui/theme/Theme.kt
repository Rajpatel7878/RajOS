package com.rajos.android.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val RajOSLightColors = lightColorScheme()
private val RajOSDarkColors = darkColorScheme()

@Composable
fun RajOSTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) RajOSDarkColors else RajOSLightColors,
        content = content
    )
}
