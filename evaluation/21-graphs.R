#!/usr/bin/env R

# usage:
# export FILENAME_PREFIX="one_"
# export TITLE_POSTFIX=" [Experiment one]"
# cat 21-graphs.R | sed s:==FILENAME==:try.db: | R --no-save --quiet

## install.packages("PACKAGE-NAME")
library(ggplot2)
library(RSQLite)
library(scales)
library(reshape2)

filename_prefix <- Sys.getenv("FILENAME_PREFIX")
title_postfix <- Sys.getenv("TITLE_POSTFIX")

# database connection
con <- dbConnect("SQLite", dbname="==FILENAME==")
#con <- dbConnect("SQLite", dbname="~/remote/scratch/pbschoon/resultdir-dissemination-random/try.db")

# CPU
res <- dbSendQuery(con, statement=paste("SELECT peer.hostname AS hostname, cpu.timestamp AS timestamp, cpu.percentage / 100.0 AS percentage FROM cpu JOIN peer ON peer.id = cpu.peer"))
DATA <- data.frame(fetch(res, n=-1))
sqliteCloseResult(res)

p <- ggplot(DATA, aes(timestamp, percentage, color=hostname))
p <- p + labs(title=paste("CPU usage", title_postfix), x="Time (seconds)", y="Usage (percentage)")
p <- p + geom_point(shape=".")
p <- p + geom_smooth(method="auto")
p <- p + scale_y_continuous(labels=percent)
ggsave(filename=paste(filename_prefix, "cpu.png", sep=""), plot=p)

# memory
res <- dbSendQuery(con, statement=paste("SELECT timestamp, rss, vms FROM memory"))
DATA <- data.frame(fetch(res, n=-1))
sqliteCloseResult(res)

p <- ggplot(DATA, aes(timestamp, vms))
p <- p + labs(title=paste("Virtual Memory Size", title_postfix), x="Time (seconds)", y="Usage (bytes)")
p <- p + geom_point(shape=".")
p <- p + geom_smooth(method="auto")
p <- p + scale_y_continuous(labels=comma)
ggsave(filename=paste(filename_prefix, "memory.png", sep=""), plot=p)

# bandwidth
res <- dbSendQuery(con, statement=paste("SELECT timestamp, up, down FROM bandwidth_rate"))
DATA <- data.frame(fetch(res, n=-1))
DATA <- melt(DATA, id=c("timestamp"))
sqliteCloseResult(res)

p <- ggplot(DATA, aes(timestamp, value, color=variable))
p <- p + labs(title=paste("Bandwidth rate", title_postfix), x="Time (seconds)", y="Usage (bytes)")
p <- p + geom_point(shape=".")
p <- p + geom_smooth(method="auto")
p <- p + scale_y_continuous(labels=comma)
ggsave(filename=paste(filename_prefix, "bandwidth.png", sep=""), plot=p)

# packet success and drop
res <- dbSendQuery(con, statement=paste("SELECT timestamp, drop_count, delay_count, delay_send, delay_success, delay_timeout, success_count, received_count FROM bandwidth"))
DATA <- data.frame(fetch(res, n=-1))
DATA <- melt(DATA, id=c("timestamp"))
sqliteCloseResult(res)

p <- ggplot(DATA, aes(timestamp, value, color=variable))
p <- p + labs(title=paste("Ability to process received packets", title_postfix), x="Time (seconds)", y="Counters")
p <- p + geom_point(shape=".")
p <- p + geom_smooth(method="auto")
p <- p + scale_y_continuous(labels=comma)
ggsave(filename=paste(filename_prefix, "success_and_loss.png", sep=""), plot=p)

# dissemination
res <- dbSendQuery(con, statement="SELECT timestamp, peer FROM received ORDER BY timestamp")
DATA <- data.frame(fetch(res, n=-1))
DATA <- within(DATA, { received <- ave(timestamp, peer, FUN=seq)})
sqliteCloseResult(res)

p <- ggplot(DATA)
p <- p + labs(title=paste("Download progress", title_postfix), x="Time (seconds)", y="Records received")
p <- p + annotate("segment", x=0, y=0, xend=3000/(27/5), yend=3000)
p <- p + geom_step(aes(x=timestamp, y=received, color=peer))
p <- p + scale_y_continuous(labels=comma)
ggsave(filename=paste(filename_prefix, "download_progress.png", sep=""), plot=p)

# quit
quit(save="no")
