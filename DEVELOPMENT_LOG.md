### [2025-12-05 12:00:00] [Event] Fixed Missing Table in New DB
- **Issue**: `scraping_rules` table was missing in `app_v2.db`, causing errors in Rule Library.
  - Reason: The migration for `ScrapingRule` model was likely never generated or applied in the previous DB lifecycle, or lost in the switch.
- **Action**: Generated new migration and upgraded database.
  - Command: `flask db migrate -m "Add ScrapingRule model"`
  - Command: `flask db upgrade`
- **Result**: `scraping_rules` table created. Rule Library functions should now work.
