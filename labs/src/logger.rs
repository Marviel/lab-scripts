use std::fs::{self, File};
use std::io::{self, Write};
use std::path::Path;

pub fn preexec(session_dir: &Path, cmd_count: usize, cmd: &str) {
    let cmd_dir = session_dir.join(format!("{}__{}", cmd_count, cmd));
    fs::create_dir_all(&cmd_dir).unwrap();

    let mut f = File::create(cmd_dir.join("command.txt")).unwrap();
    f.write_all(cmd.as_bytes()).unwrap();
}

pub fn precmd(session_dir: &Path, cmd_count: usize) {
    let cmd_dir = session_dir.join(format!("{}__{}", cmd_count, "last_command"));
    // Capture and append stdout, stderr, and full.txt here
    // Implementation depends on how you capture these streams
}
