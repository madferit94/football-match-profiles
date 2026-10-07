# Match context and outcomes

[데이터 목차 / Data index](../README.md)

Scope: **2019/20–2024/25**, match dates **2019-08-09–2025-05-25**. Ranges and missing counts are computed from the included files.

Labels follow the thesis, code, and column names. A provider-field mapping has not been recovered. Attempted versus successful passes, long balls, crosses, dribbles, tackles, and spatial definitions of progression require source verification.

## `league` — League

- Meaning: League
- Unit/encoding: label
- Clustering input: no
- File: input + labeled
- Stored dtype: `object`
- Example values: EPL, LaLiga, Bundesliga, SerieA, Ligue1
- Missing: 0 / 21,394 rows

## `match_id` — Match identifier

- Meaning: Match identifier
- Unit/encoding: ID
- Clustering input: no
- File: input + labeled
- Stored dtype: `int64`
- Observed range: 11643 – 28353
- Missing: 0 / 21,394 rows
- Uniqueness was checked on `(league, match_id, team)`; provider ID provenance remains unresolved.

## `season` — Season

- Meaning: Season
- Unit/encoding: label
- Clustering input: no
- File: input + labeled
- Stored dtype: `object`
- Example values: 2019_2020, 2020_2021, 2021_2022, 2022_2023, 2023_2024, 2024_2025
- Missing: 0 / 21,394 rows

## `date` — Match date

- Meaning: Match date
- Unit/encoding: YYYY-MM-DD
- Clustering input: no
- File: input + labeled
- Stored dtype: `object`
- Example values: 2019-08-09, 2019-08-10, 2019-08-11, 2019-08-17, 2019-08-18, 2019-08-19
- Missing: 0 / 21,394 rows

## `team` — Team

- Meaning: Team
- Unit/encoding: label
- Clustering input: no
- File: input + labeled
- Stored dtype: `object`
- Example values: Liverpool, Bournemouth, Burnley, Crystal Palace, Tottenham Hotspur, Watford
- Missing: 0 / 21,394 rows

## `opponent` — Opponent

- Meaning: Opponent
- Unit/encoding: label
- Clustering input: no
- File: input + labeled
- Stored dtype: `object`
- Example values: Norwich City, Sheffield United, Southampton, Everton, Aston Villa, Brighton & Hove Albion
- Missing: 0 / 21,394 rows

## `team_score` — Team goals

- Meaning: Team goals
- Unit/encoding: count
- Clustering input: no
- File: input + labeled
- Stored dtype: `int64`
- Observed range: 0 – 9
- Missing: 0 / 21,394 rows

## `opponent_score` — Opponent goals

- Meaning: Opponent goals
- Unit/encoding: count
- Clustering input: no
- File: input + labeled
- Stored dtype: `int64`
- Observed range: 0 – 9
- Missing: 0 / 21,394 rows

## `is_home` — Home indicator

- Meaning: Home indicator
- Unit/encoding: 0/1
- Clustering input: no
- File: input
- Stored dtype: `int64`
- Observed range: 0 – 1
- Missing: 0 / 21,394 rows

## `result` — Match result

- Meaning: Match result
- Unit/encoding: W/D/L
- Clustering input: no
- File: input + labeled
- Stored dtype: `object`
- Example values: W, D, L
- Missing: 0 / 21,394 rows

## `xG` — Expected goals

- Meaning: Expected goals
- Unit/encoding: expected goals
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0 – 6.88
- Missing: 0 / 21,394 rows

