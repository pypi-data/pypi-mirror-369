# Grit Guardian 🐉

Grit Guardian is a command-line habit tracking application that gamifies your routines with an interactive virtual companion (Guardian).
Don't let your Guardian's mood get sour: stay consistent and build lasting habits!

[![Tests](https://github.com/pi-weiss/grit-guardian/workflows/Tests/badge.svg)](https://github.com/pi-weiss/grit-guardian/actions)
[![Coverage](https://codecov.io/gh/pi-weiss/grit-guardian/branch/main/graph/badge.svg)](https://codecov.io/gh/pi-weiss/grit-guardian)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads)
[![license: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
## ✨ Features


- 📊 **Habit Tracking**: Track daily and weekly habits with completion timestamps
- 🔥 **Streak Analytics**: Calculate current and longest streaks with completion rates
- 🐉 **Virtual Companion**: Interactive Guardian with mood based on your performance
- 📅 **Weekly Progress**: ASCII table showing week-at-a-glance habit completion
- 📈 **Analytics Dashboard**: Identify struggling habits and track overall progress
- 🎯 **Sample Data**: Quick-start with pre-configured habit examples
- 💾 **Local Storage**: SQLite database with automatic backup and recovery
- 🎨 **Beautiful CLI**: Colorful, emoji-rich interface with clear visual feedback

## 🚀 Quick Start

### Installation

#### Option 1: Install from PyPI (Recommended)
```bash
pip install grit-guardian
```

#### Option 2: Install from Source
```bash
git clone https://github.com/pi-weiss/grit-guardian.git
cd grit-guardian
poetry install
```

### First Run

1. **Initialize with sample data:**
   ```bash
   grit-guardian init
   # or use the short alias
   gg init
   ```

2. **View your habits:**
   ```bash
   gg list
   ```

3. **Check today's status:**
   ```bash
   gg status
   ```

4. **Complete a habit:**
   ```bash
   gg complete "Morning Reading"
   ```

5. **Meet your Guardian:**
   ```bash
   gg pet
   ```

## 📖 Usage Guide

### Core Commands

#### Habit Management
```bash
# Add a new habit
gg add "Exercise" "30 minutes of physical activity" daily
gg add "Weekly Planning" "Review and plan the week" weekly

# List all habits
gg list

# Delete a habit (with confirmation)
gg delete "Exercise"
```

#### Completion Tracking
```bash
# Mark a habit as completed
gg complete "Exercise"

# View today's status
gg status

# Check current streaks and completion rates
gg streaks
```

#### Analytics & Progress
```bash
# View weekly progress table
gg weekly

# Identify habits you're struggling with
gg struggled
gg struggled --since 14  # Check last 14 days

# Visit your Guardian pet
gg pet
```

#### Quick Reference
```bash
# Get help for any command
gg --help
gg add --help

# Initialize sample data (first time only)
gg init
```

## 🔧 Configuration

### Data Storage

Habits are stored in SQLite database located at:
- **Linux/macOS**: `~/.config/grit-guardian/habits.db`
- **Windows**: `%APPDATA%\grit-guardian\habits.db`

### Backup and Recovery

The application automatically:
- Creates database backups before schema changes
- Validates database integrity on startup
- Provides recovery options for corrupted databases

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Start building better habits today with Grit Guardian! 🐉✨**
