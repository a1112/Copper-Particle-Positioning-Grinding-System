#include <windows.h>

int APIENTRY wWinMain(HINSTANCE hInstance, HINSTANCE, LPWSTR, int)
{
    MessageBoxW(nullptr,
                L"C++ launcher started.",
                L"UiLauncher",
                MB_OK | MB_ICONINFORMATION);
    return 0;
}

