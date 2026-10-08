/**
 * Project Intelligence — Install Manifest Manager & Safe Reverter
 * Tracks created files, directory structures, and non-destructive file modifications.
 * Conformance: Zero external npm dependencies.
 */

const fs = require('fs');
const path = require('path');

const BEGIN_MARKER = '<!-- BEGIN PROJECT-INTELLIGENCE -->';
const END_MARKER = '<!-- END PROJECT-INTELLIGENCE -->';
const MARKER_REGEX = /<!-- BEGIN PROJECT-INTELLIGENCE -->[\s\S]*?<!-- END PROJECT-INTELLIGENCE -->/m;

function getManifestDir(targetDir) {
  return path.join(targetDir, '.project-intelligence');
}

function getManifestPath(targetDir) {
  return path.join(getManifestDir(targetDir), 'install-manifest.json');
}

function loadManifest(targetDir) {
  const manifestPath = getManifestPath(targetDir);
  if (!fs.existsSync(manifestPath)) {
    return null;
  }
  try {
    const raw = fs.readFileSync(manifestPath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    return null;
  }
}

function saveManifest(targetDir, manifestData) {
  const manifestDir = getManifestDir(targetDir);
  if (!fs.existsSync(manifestDir)) {
    fs.mkdirSync(manifestDir, { recursive: true });
  }
  const manifestPath = getManifestPath(targetDir);
  fs.writeFileSync(manifestPath, JSON.stringify(manifestData, null, 2) + '\n', 'utf8');
}

function deleteManifest(targetDir) {
  const manifestPath = getManifestPath(targetDir);
  if (fs.existsSync(manifestPath)) {
    fs.unlinkSync(manifestPath);
  }
  const manifestDir = getManifestDir(targetDir);
  if (fs.existsSync(manifestDir)) {
    try {
      const remaining = fs.readdirSync(manifestDir);
      if (remaining.length === 0) {
        fs.rmdirSync(manifestDir);
      }
    } catch {
      // Ignore directory cleanup error if not empty
    }
  }
}

/**
 * Injects non-destructive marker block into content.
 * Replaces existing block if present, or appends cleanly.
 */
function injectMarkerBlock(existingContent, blockBody) {
  const wrappedBlock = `${BEGIN_MARKER}\n${blockBody.trim()}\n${END_MARKER}`;
  if (!existingContent || existingContent.trim().length === 0) {
    return wrappedBlock + '\n';
  }
  if (MARKER_REGEX.test(existingContent)) {
    return existingContent.replace(MARKER_REGEX, wrappedBlock);
  }
  const separator = existingContent.endsWith('\n') ? '\n' : '\n\n';
  return `${existingContent}${separator}${wrappedBlock}\n`;
}

/**
 * Removes marker block from content.
 */
function removeMarkerBlock(content) {
  if (!content) return '';
  if (!MARKER_REGEX.test(content)) return content;
  const cleaned = content.replace(MARKER_REGEX, '').trim();
  return cleaned.length > 0 ? cleaned + '\n' : '';
}

/**
 * Reverts installed files and merged configuration according to install manifest.
 */
function revertInstallation(targetDir, dryRun = false) {
  const manifest = loadManifest(targetDir);
  if (!manifest) {
    return {
      success: false,
      message: 'No install manifest found in .project-intelligence/install-manifest.json',
      revertedFiles: [],
      removedFiles: [],
      removedDirectories: [],
    };
  }

  const revertedFiles = [];
  const removedFiles = [];
  const removedDirectories = [];

  // 1. Revert modified files
  if (Array.isArray(manifest.modifiedFiles)) {
    for (const mod of manifest.modifiedFiles) {
      const filePath = path.resolve(targetDir, mod.path);
      if (fs.existsSync(filePath)) {
        if (!mod.existedBefore) {
          // File was created by us, remove it completely
          if (!dryRun) {
            fs.unlinkSync(filePath);
          }
          removedFiles.push(mod.path);
        } else if (mod.backupContent !== undefined && mod.backupContent !== null) {
          // Restore exact backup content
          if (!dryRun) {
            fs.writeFileSync(filePath, mod.backupContent, 'utf8');
          }
          revertedFiles.push(mod.path);
        } else {
          // Fallback: strip marker block or remove our JSON keys
          const currentContent = fs.readFileSync(filePath, 'utf8');
          if (MARKER_REGEX.test(currentContent)) {
            const stripped = removeMarkerBlock(currentContent);
            if (stripped.trim().length === 0) {
              if (!dryRun) fs.unlinkSync(filePath);
              removedFiles.push(mod.path);
            } else {
              if (!dryRun) fs.writeFileSync(filePath, stripped, 'utf8');
              revertedFiles.push(mod.path);
            }
          } else if (filePath.endsWith('.json')) {
            // Revert deep merged json
            try {
              const data = JSON.parse(currentContent);
              if (data.mcpServers && data.mcpServers['project-intelligence']) {
                delete data.mcpServers['project-intelligence'];
              }
              if (data.hooks) {
                for (const hookType of Object.keys(data.hooks)) {
                  if (Array.isArray(data.hooks[hookType])) {
                    data.hooks[hookType] = data.hooks[hookType].filter(
                      (h) => !h.command.includes('project-intelligence') && !h.command.includes('.claude/hooks/')
                    );
                    if (data.hooks[hookType].length === 0) {
                      delete data.hooks[hookType];
                    }
                  }
                }
                if (Object.keys(data.hooks).length === 0) {
                  delete data.hooks;
                }
              }
              if (Object.keys(data).length === 0) {
                if (!dryRun) fs.unlinkSync(filePath);
                removedFiles.push(mod.path);
              } else {
                if (!dryRun) fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
                revertedFiles.push(mod.path);
              }
            } catch {
              // Ignore json parse error
            }
          }
        }
      }
    }
  }

  // 2. Remove files created exclusively by the installer
  if (Array.isArray(manifest.createdFiles)) {
    for (const relPath of manifest.createdFiles) {
      const fullPath = path.resolve(targetDir, relPath);
      if (fs.existsSync(fullPath)) {
        if (!dryRun) {
          fs.unlinkSync(fullPath);
        }
        removedFiles.push(relPath);
      }
    }
  }

  // 3. Remove created directories in reverse order
  if (Array.isArray(manifest.createdDirectories)) {
    const dirs = [...manifest.createdDirectories].sort((a, b) => b.length - a.length);
    for (const relDir of dirs) {
      const fullDir = path.resolve(targetDir, relDir);
      if (fs.existsSync(fullDir)) {
        try {
          const contents = fs.readdirSync(fullDir);
          if (contents.length === 0) {
            if (!dryRun) {
              fs.rmdirSync(fullDir);
            }
            removedDirectories.push(relDir);
          }
        } catch {
          // Directory not empty or failed to remove
        }
      }
    }
  }

  // 4. Delete manifest itself
  if (!dryRun) {
    deleteManifest(targetDir);
  }

  return {
    success: true,
    message: 'Installation cleanly reverted.',
    revertedFiles,
    removedFiles,
    removedDirectories,
  };
}

module.exports = {
  BEGIN_MARKER,
  END_MARKER,
  getManifestDir,
  getManifestPath,
  loadManifest,
  saveManifest,
  deleteManifest,
  injectMarkerBlock,
  removeMarkerBlock,
  revertInstallation,
};
