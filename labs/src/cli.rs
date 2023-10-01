use clap::{App, Arg, SubCommand};

pub fn build_cli() -> App<'static, 'static> {
    App::new("labs")
        .subcommand(
            SubCommand::with_name("hist")
                .arg(Arg::with_name("n").takes_value(true).short("n"))
                .arg(Arg::with_name("prev").takes_value(true).long("prev")),
        )
        .subcommand(SubCommand::with_name("prev"))
}
