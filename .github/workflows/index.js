import { spawn } from 'child_process';
import fetch from 'node-fetch';
import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';

const FILEPATH = core.getInput("image_path");
const THM_USERNAME = core.getInput("username");
const COMMITTER_USERNAME = core.getInput('committer_username') || 'github-actions[bot]';
const COMMITTER_EMAIL = core.getInput('committer_email') || 'github-actions[bot]@users.noreply.github.com';
const COMMIT_MESSAGE = core.getInput('commit_message') || 'Update TryHackMe badge';

// Utility to execute shell commands
const execShellCommand = async (cmd, args = []) => {
  const process = spawn(cmd, args, { stdio: 'pipe' });
  let data = '';

  process.stdout.on('data', (chunk) => data += chunk);
  process.stderr.on('data', (chunk) => data += chunk);

  return new Promise((resolve, reject) => {
    process.on('exit', (code) => {
      if (code === 0) resolve(data);
      else reject(new Error(`Failed with code ${code}: ${data}`));
    });
  });
};

// Download and update the TryHackMe badge
const updateTryHackMeBadge = async () => {
  try {
    const imagePath = path.join(process.cwd(), FILEPATH);
    const imageURL = `https://tryhackme-badges.s3.amazonaws.com/${THM_USERNAME}.png`;

    // Fetch and save the image
    const response = await fetch(imageURL);
    if (!response.ok) throw new Error(`Failed to fetch image: ${response.statusText}`);
    const stream = fs.createWriteStream(imagePath);
    await new Promise((resolve, reject) => {
      response.body.pipe(stream);
      response.body.on('error', reject);
      stream.on('finish', resolve);
    });

    // Git configuration
    await execShellCommand('git', ['config', '--global', 'user.name', COMMITTER_USERNAME]);
    await execShellCommand('git', ['config', '--global', 'user.email', COMMITTER_EMAIL]);

    // Git operations
    await execShellCommand('git', ['add', FILEPATH]);
    try {
      await execShellCommand('git', ['commit', '-m', COMMIT_MESSAGE]);
      await execShellCommand('git', ['push']);
    } catch (error) {
      if (!error.message.includes('nothing to commit')) throw error;
      console.log('No changes detected, skipping push.');
    }
  } catch (error) {
    core.setFailed(`Action failed with error: ${error}`);
  }
};

updateTryHackMeBadge();
