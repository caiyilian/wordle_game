import { app, BrowserWindow } from 'electron'
import { resolve } from 'path'

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 900,
    minWidth: 600,
    minHeight: 700,
    title: 'Web Wordle',
    webPreferences: {
      preload: resolve(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // In dev, load Vite dev server; in production, load built files
  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
    win.webContents.openDevTools()
  } else {
    win.loadFile(resolve(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
