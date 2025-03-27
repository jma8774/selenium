import { app, BrowserWindow } from 'electron';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url'
import { spawn } from 'child_process';
import log from 'electron-log';

// Configure electron-log
log.transports.file.level = 'info';
log.transports.console.level = 'info';

// needed in case process is undefined under Linux
const platform = process.platform || os.platform();

const currentDir = fileURLToPath(new URL('.', import.meta.url));

let mainWindow: BrowserWindow | undefined;

async function createWindow() {
  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    icon: path.resolve(currentDir, 'icons/icon.png'), // tray icon
    width: 1366,
    height: 768,
    useContentSize: true,
    webPreferences: {
      contextIsolation: true,
      // More info: https://v2.quasar.dev/quasar-cli-vite/developing-electron-apps/electron-preload-script
      preload: path.resolve(
        currentDir,
        path.join(process.env.QUASAR_ELECTRON_PRELOAD_FOLDER, 'electron-preload' + process.env.QUASAR_ELECTRON_PRELOAD_EXTENSION)
      ),
    },
  });

  if (process.env.DEV) {
    await mainWindow.loadURL(process.env.APP_URL);
  } else {
    await mainWindow.loadFile('index.html');
  }

  if (process.env.DEBUGGING) {
    // if on DEV or Production with debug enabled
    mainWindow.webContents.openDevTools();
  } else {
    // we're on production; no access to devtools pls
    mainWindow.webContents.on('devtools-opened', () => {
      mainWindow?.webContents.closeDevTools();
    });
  }
  // Run Python script
  // const pythonProcess = runPythonScript();

  mainWindow.on('closed', () => {
    mainWindow = undefined;
    // pythonProcess?.kill();
  });

}

function runPythonScript() {
  const pythonScriptPath = path.resolve(process.cwd(), '../backend/main.py');
  log.info("Current directory:", process.cwd());
  log.info("Python script path:", pythonScriptPath);

  try {
    const pythonProcess = spawn('python', [pythonScriptPath], {
      stdio: 'pipe',
      shell: false  // Don't need shell now
    });

    // Handle process events
    pythonProcess.stdout.on('data', (data) => {
      log.info('Python stdout:', data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      log.warn('Python stderr:', data.toString());
    });

    pythonProcess.on('error', (error) => {
      log.error('Failed to start Python process:', error);
    });

    pythonProcess.on('close', (code) => {
      log.info(`Python process exited with code ${code}`);
    });

    return pythonProcess;

  } catch (error) {
    log.error('Error running Python script:', error);
  }

  return null;
}

void app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === undefined) {
    void createWindow();
  }
});
