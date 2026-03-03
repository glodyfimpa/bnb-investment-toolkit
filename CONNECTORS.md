# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user
connects in that category. Plugins are tool-agnostic: they describe
workflows in terms of categories rather than specific products.

## Connectors for this plugin

| Category | Placeholder | Options |
|----------|-------------|---------|
| Project tracker | `~~project tracker` | Notion, Airtable, Google Sheets |

The property-acquisition-tracker skill saves scouted listings to a project tracker database.
Any tool that supports structured database entries (properties, fields, status values) works.

If using Notion, create a database with the schema described in the property-acquisition-tracker skill (fields: Name, URL, Price, Size, Zone, Rooms, Floor, Score, Investment Status, Source, Scan Date, Notes).
