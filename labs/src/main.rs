mod cli;
mod logger;

use clap::App;
use std::path::Path;

fn main() {
    let session_dir = Path::new("/path/to/sessions/session_timestamp");
    let cmd_count = 0; // Increment this per command run

    let matches = cli::build_cli().get_matches();

    if let Some(matches) = matches.subcommand_matches("hist") {
        // Handle hist
    } else if matches.subcommand_matches("prev").is_some() {
        // Handle prev
    } else {
        // Handle logging
        if let Some(cmd) = std::env::args().nth(2) {
            logger::preexec(&session_dir, cmd_count, &cmd);
        } else {
            logger::precmd(&session_dir, cmd_count);
        }
    }
}
