# SignalDesk Database Schema (V1)

## Overview

SignalDesk is a customer risk intelligence platform that predicts which customer accounts are at risk of escalation.

The V1 schema supports:

* customer account storage
* historical signal snapshots
* calculated risk scores
* configurable scoring models
* configurable scoring rules
* future reporting and trend analysis

The schema contains five core tables:

* `accounts`
* `account_signal_snapshots`
* `scoring_configs`
* `scoring_rules`
* `risk_scores`

---

## Data Model Flow

At a high level:

1. Accounts are stored in `accounts`
2. Daily operational signals are captured in `account_signal_snapshots`
3. Scoring logic is defined via:

   * `scoring_configs`
   * `scoring_rules`
4. The scoring engine computes results and stores them in `risk_scores`

---

## ER Diagram

```mermaid
erDiagram
    accounts ||--o{ account_signal_snapshots : has
    scoring_configs ||--o{ scoring_rules : defines
    accounts ||--o{ risk_scores : has
    scoring_configs ||--o{ risk_scores : produces
    account_signal_snapshots ||--o{ risk_scores : scored_as

    accounts {
        int account_id PK
        varchar account_name
        varchar segment
        numeric arr_usd
        boolean strategic_account
        timestamp created_at
    }

    account_signal_snapshots {
        int snapshot_id PK
        int account_id FK
        date snapshot_date
        int days_to_renewal
        int open_tickets_30d
        int reopened_tickets_30d
        numeric avg_first_response_hrs
        numeric avg_resolution_hrs
        int sev1_tickets_30d
        numeric sentiment_score
        numeric csat_avg_90d
        numeric usage_change_pct_30d
        numeric login_change_pct_30d
        boolean known_bug_flag
        int csm_health_score
        timestamp created_at
    }

    scoring_configs {
        int scoring_config_id PK
        varchar config_name
        text description
        boolean is_active
        boolean is_default
        boolean is_editable
        timestamp created_at
    }

    scoring_rules {
        int scoring_rule_id PK
        int scoring_config_id FK
        varchar metric_name
        numeric weight
        numeric threshold_low
        numeric threshold_medium
        numeric threshold_high
        numeric points_low
        numeric points_medium
        numeric points_high
        numeric points_critical
        timestamp created_at
    }

    risk_scores {
        int risk_score_id PK
        int account_id FK
        int snapshot_id FK
        int scoring_config_id FK
        numeric total_score
        varchar risk_band
        varchar top_driver_1
        varchar top_driver_2
        varchar top_driver_3
        varchar recommended_action_1
        varchar recommended_action_2
        varchar recommended_action_3
        timestamp scored_at
    }

---

## 1. accounts

Stores master account information.

| Column            | Type                                         | Description                                    |
| ----------------- | -------------------------------------------- | ---------------------------------------------- |
| account_id        | SERIAL PRIMARY KEY                           | Unique internal ID for each account            |
| account_name      | VARCHAR(255) NOT NULL UNIQUE                 | Customer or company name                       |
| segment           | VARCHAR(50) NOT NULL                         | Customer segment (SMB, Mid-Market, Enterprise) |
| arr_usd           | NUMERIC(12,2) NOT NULL DEFAULT 0             | Annual recurring revenue in USD                |
| strategic_account | BOOLEAN NOT NULL DEFAULT FALSE               | Indicates strategic/high-priority accounts     |
| created_at        | TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP | Account creation timestamp                     |

### Purpose

This is the core customer registry table. Each account appears exactly once.

---

## 2. account_signal_snapshots

Stores historical signal data for each account.

Each row represents a snapshot of one account on one date.

| Column                 | Type                                         | Description                 |
| ---------------------- | -------------------------------------------- | --------------------------- |
| snapshot_id            | SERIAL PRIMARY KEY                           | Unique ID for each snapshot |
| account_id             | INTEGER NOT NULL                             | FK → accounts.account_id    |
| snapshot_date          | DATE NOT NULL                                | Snapshot date               |
| days_to_renewal        | INTEGER NOT NULL                             | Days until renewal          |
| open_tickets_30d       | INTEGER NOT NULL DEFAULT 0                   | Open tickets (30d)          |
| reopened_tickets_30d   | INTEGER NOT NULL DEFAULT 0                   | Reopened tickets (30d)      |
| avg_first_response_hrs | NUMERIC(8,2) NOT NULL DEFAULT 0              | Avg first response time     |
| avg_resolution_hrs     | NUMERIC(8,2) NOT NULL DEFAULT 0              | Avg resolution time         |
| sev1_tickets_30d       | INTEGER NOT NULL DEFAULT 0                   | Critical tickets (30d)      |
| sentiment_score        | NUMERIC(5,2) NOT NULL                        | Range: -1.00 to 1.00        |
| csat_avg_90d           | NUMERIC(3,2) NOT NULL                        | Range: 1.00 to 5.00         |
| usage_change_pct_30d   | NUMERIC(6,2) NOT NULL                        | Usage change (%)            |
| login_change_pct_30d   | NUMERIC(6,2) NOT NULL                        | Login change (%)            |
| known_bug_flag         | BOOLEAN NOT NULL DEFAULT FALSE               | Known bug impacting account |
| csm_health_score       | INTEGER NOT NULL                             | Range: 0–100                |
| created_at             | TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP | Snapshot creation time      |

### Constraints

* One snapshot per account per day
* Numeric ranges enforced via CHECK constraints

### Purpose

This is the **core fact table** representing account health over time.

---

## 3. scoring_configs

Stores scoring model configurations.

| Column            | Type                                         | Description           |
| ----------------- | -------------------------------------------- | --------------------- |
| scoring_config_id | SERIAL PRIMARY KEY                           | Unique ID             |
| config_name       | VARCHAR(100) NOT NULL UNIQUE                 | Name of scoring model |
| description       | TEXT                                         | Optional description  |
| is_active         | BOOLEAN NOT NULL DEFAULT FALSE               | Active runtime config |
| is_default        | BOOLEAN NOT NULL DEFAULT FALSE               | Default system config |
| is_editable       | BOOLEAN NOT NULL DEFAULT TRUE                | Editable by users     |
| created_at        | TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP | Creation timestamp    |

### Purpose

Enables:

* default system model
* active runtime model
* editable vs locked configs
* future multi-model support

### Examples

* Default V1 Model
* Enterprise Heavy Model
* Renewal Sensitive Model

---

## 4. scoring_rules

Defines how each metric contributes to the score.

| Column            | Type                                         | Description                            |
| ----------------- | -------------------------------------------- | -------------------------------------- |
| scoring_rule_id   | SERIAL PRIMARY KEY                           | Unique ID                              |
| scoring_config_id | INTEGER NOT NULL                             | FK → scoring_configs.scoring_config_id |
| metric_name       | VARCHAR(100) NOT NULL                        | Metric being scored                    |
| weight            | NUMERIC(6,2) NOT NULL DEFAULT 1.0            | Weight multiplier                      |
| threshold_low     | NUMERIC(10,2)                                | Low threshold                          |
| threshold_medium  | NUMERIC(10,2)                                | Medium threshold                       |
| threshold_high    | NUMERIC(10,2)                                | High threshold                         |
| points_low        | NUMERIC(6,2) NOT NULL DEFAULT 0              | Points (low range)                     |
| points_medium     | NUMERIC(6,2) NOT NULL DEFAULT 0              | Points (medium range)                  |
| points_high       | NUMERIC(6,2) NOT NULL DEFAULT 0              | Points (high range)                    |
| points_critical   | NUMERIC(6,2) NOT NULL DEFAULT 0              | Points (critical range)                |
| created_at        | TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP | Creation timestamp                     |

### Purpose

Makes scoring fully configurable without code changes.

Each metric defines:

* thresholds
* scoring bands
* weights

### Notes

* One rule per metric per scoring config

---

## 5. risk_scores

Stores computed risk outputs.

| Column               | Type                                         | Description                               |
| -------------------- | -------------------------------------------- | ----------------------------------------- |
| risk_score_id        | SERIAL PRIMARY KEY                           | Unique ID                                 |
| account_id           | INTEGER NOT NULL                             | FK → accounts.account_id                  |
| snapshot_id          | INTEGER NOT NULL                             | FK → account_signal_snapshots.snapshot_id |
| scoring_config_id    | INTEGER NOT NULL                             | FK → scoring_configs.scoring_config_id    |
| total_score          | NUMERIC(5,2) NOT NULL                        | Final score (0–100)                       |
| risk_band            | VARCHAR(20) NOT NULL                         | Low, Medium, High, Critical               |
| top_driver_1         | VARCHAR(255)                                 | Primary risk driver                       |
| top_driver_2         | VARCHAR(255)                                 | Secondary driver                          |
| top_driver_3         | VARCHAR(255)                                 | Third driver                              |
| recommended_action_1 | VARCHAR(255)                                 | Action 1                                  |
| recommended_action_2 | VARCHAR(255)                                 | Action 2                                  |
| recommended_action_3 | VARCHAR(255)                                 | Action 3                                  |
| scored_at            | TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP | Score timestamp                           |

### Purpose

This is the **final output layer** powering:

* dashboards
* reporting
* trend analysis
* explanations and recommendations

### Notes

* One score per snapshot per scoring config

---

## Relationships

* `accounts` → one-to-many → `account_signal_snapshots`
* `scoring_configs` → one-to-many → `scoring_rules`
* `account_signal_snapshots` → one-to-many → `risk_scores`
* `accounts` → one-to-many → `risk_scores`
* `scoring_configs` → one-to-many → `risk_scores`

---

## Scoring Model Notes (Important)

* Scores are computed using:

  * snapshot data
  * active scoring config
  * associated scoring rules

* Each metric:

  * is evaluated against thresholds
  * assigned points
  * multiplied by weight

* Final score is normalized to a 0–100 scale and mapped to a risk band.

---

## Known V1 Considerations

* `csat_avg_90d` exists in the schema and data model but may not yet be fully integrated into scoring logic depending on engine configuration.
* Schema is designed to support:

  * multiple scoring models
  * historical comparisons
  * future ML-based scoring extensions

---

## Load Order (Recommended)

1. `schema.sql`
2. `seed_defaults.sql`
3. `seed_demo_data.sql`
4. `seed_historical_snapshots.sql`
5. Run scoring engine

---

If you want next step, I can:

* add a **Mermaid ER diagram** (super clean for GitHub rendering), or
* align this doc **exactly with your scoring engine code (metric-by-metric)** so it becomes investor/demo-ready.
