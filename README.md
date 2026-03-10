# Tomato Clock Tracker 🍅

## Background

This is a small personal project that records Pomodoro (tomato clock) sessions using a 
[Particle P2](https://store.particle.io/products/p2) device and a 
[Particle Tachyon](https://store.particle.io/products/tachyon) backend.
> *"Knowledge is not free --- you have to pay attention."*

In today's world, it is becoming harder to stay focused. We are
surrounded by smart devices, notifications, and endless streams of
distraction.

At the beginning of **2026**, I decided to take my attention back.\
So I built my own **physical tomato clock**.

The idea is simple:\
when I want to focus, I press a button and commit to **30 minutes of
uninterrupted work**.

------------------------------------------------------------------------

## Features

This project intentionally keeps things simple.\
It has **only two features**:

1.  **Start a 30-minute focus session** by pressing a button.
2.  **Receive a daily email report** showing how many focus sessions
    were completed.

That's it. No apps, no notifications, no distractions.

------------------------------------------------------------------------

## System Architecture

To keep the design simple:

-   **Particle P2** acts as the local controller.
-   **Tachyon** acts as the backend subscriber.


```
    Button press
        ↓
    Particle P2
        ↓
    Particle Cloud (event publish)
        ↓
    Tachyon subscriber
        ↓
    SQLite database
        ↓
    Weekly report script (cron)
        ↓
    Email summary
```

### Components

**Device** - Particle **P2** - Button input - Optional LCD / progress
bar display

**Backend** - Tachyon - Python scripts - SQLite
database - Cron scheduler

------------------------------------------------------------------------

## Reporting

One feature that distinguishes this tomato clock from others is the
**daily email report**.

Every day I receive an email summarizing:

-   total focus sessions
-   total focus time
-   daily breakdown

Example report:

    🍅 Tomato Clock Weekly Report

    Total sessions: 66
    Focus time: 1980 minutes

    Daily breakdown (Mon → Sun):

    Mon | ████                 8
    Tue | ███████              14
    Wed | ███████████          23
    Thu | ███████████████      31
    Fri | ██                   4
    Sat |                      0
    Sun |                      0

    
> 💡 **Motivation**  
> Checking this report has become a small reward that motivates me to keep improving my focus.




------------------------------------------------------------------------

## Repository Structure

    tomato_clock/
    │
    ├── subscriber.py
    ├── report_and_email.py
    ├── requirements.txt
    ├── tomato.db
    ├── report.log
    └── README.md

------------------------------------------------------------------------

## Requirements

Python 3.10+

Install dependencies:

``` bash
pip install -r requirements.txt
```

Typical dependencies:

    requests
    sseclient-py
    matplotlib

------------------------------------------------------------------------

## Running the Subscriber

The subscriber listens to **Particle Cloud events** and writes them into
the SQLite database.

Run manually:

``` bash
python subscriber.py
```

Recommended: run as a **systemd service**.

------------------------------------------------------------------------

## Scheduling the Report

Use **cron** to send the daily/weekly email report.

Edit crontab:

``` bash
crontab -e
```

Example (Friday 18:00):

``` bash
0 18 * * FRI /home/eric/myvenv/bin/python /home/eric/tomato_clock/report_and_email.py >> /home/eric/tomato_clock/report.log 2>&1
```

------------------------------------------------------------------------

## Limitations

Most of the backend code in this project was developed with the help of
**ChatGPT**.

The most difficult part was configuring **SMTP email sending on the
Tachyon**, especially when working with providers like Outlook or
Gmail.

------------------------------------------------------------------------

## Author

Eric Yuan\
ChatGPT

------------------------------------------------------------------------

## Motivation

This project is not about building a complicated productivity tool.

It is about something much simpler:

> **Take back control of attention.**
