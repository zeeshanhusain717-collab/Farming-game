[app]
title = Farm7
package.name = farm7
package.domain = org.farm
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ogg,wav,mp3
source.exclude_dirs = .buildozer,bin,.github,.git
version = 1.0
requirements = python3==3.11.5,kivy==2.3.0,plyer
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.logcat_filters = *:S python:D
p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
