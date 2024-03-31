# See setup_prefix function in https://github.com/ValveSoftware/Proton/blob/proton_8.0/proton for more proper version

# requirements

requirements () {
  yay -S proton
  pacman -S mingw-w64-binutils mingw-w64-crt mingw-w64-gcc mingw-w64-headers mingw-w64-tools mingw-w64-winpthreads
}

# base

base () {

  cp /usr/x86_64-w64-mingw32/bin/*.dll ~/.wine/drive_c/windows/system32/
  cp /usr/i686-w64-mingw32/bin/*.dll ~/.wine/drive_c/windows/syswow64/
  cp /usr/share/steam/compatibilitytools.d/proton/dist/lib64/vkd3d/*.dll ~/.wine/drive_c/windows/system32/
  cp /usr/share/steam/compatibilitytools.d/proton/dist/lib/vkd3d/*.dll ~/.wine/drive_c/windows/syswow64/

}

# optional

regdll() {
  wine reg add 'HKEY_CURRENT_USER\Software\Wine\DllOverrides' /v $1 /d native /f
}

optional () {
  cp /usr/share/steam/compatibilitytools.d/proton/dist/lib64/wine/dxvk/*.dll ~/.wine/drive_c/windows/system32/
  cp /usr/share/steam/compatibilitytools.d/proton/dist/lib/wine/dxvk/*.dll ~/.wine/drive_c/windows/syswow64/
  cp /usr/share/steam/compatibilitytools.d/proton/dist/lib64/wine/vkd3d-proton/*.dll ~/.wine/drive_c/windows/system32/
  cp /usr/share/steam/compatibilitytools.d/proton/dist/lib/wine/vkd3d-proton/*.dll ~/.wine/drive_c/windows/syswow64/

  regdll d3d12
  regdll d3d9
  regdll d3d10core
  regdll d3d11
  regdll dxgi
}

# run scripts

requirements
export PATH=$PATH:/usr/share/steam/compatibilitytools.d/proton/dist/bin
base
optional
