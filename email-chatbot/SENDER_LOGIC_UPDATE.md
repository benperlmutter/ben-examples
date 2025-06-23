# Email Chatbot Sender Logic Update

## Overview
Updated the sender determination logic in the email chatbot application to use email domain-based classification instead of simple text matching.

## Changes Made

### 1. New Sender Logic
**Before:**
```python
sender = "Events Team" if from_header.startswith("Events") else "Guest"
```

**After:**
```python
def determine_sender(self, from_header: str) -> str:
    """Determine sender based on email domain"""
    if not from_header:
        return "Guest"
    
    # Extract email address from header (handles formats like "Name <email@domain.com>")
    email_match = re.search(r'<([^>]+)>|([^\s<>]+@[^\s<>]+)', from_header)
    if email_match:
        email_address = email_match.group(1) or email_match.group(2)
        if email_address and "@bigsurriverinn.com" in email_address.lower():
            return "BSRI Team"
    
    return "Guest"
```

### 2. Updated Sender Labels
- **Old:** "Events Team" 
- **New:** "BSRI Team"
- **Criteria:** Any email from `@bigsurriverinn.com` domain → "BSRI Team"
- **Default:** All other emails → "Guest"

### 3. Files Modified

#### `aug_collect_all_emails.py`
- Added `import re`
- Added `determine_sender()` method
- Updated sender assignment logic
- Updated statistics logging to show "BSRI Team" instead of "Events Team"

#### `aug_update_emails.py`
- Added `import re`
- Added `determine_sender()` method
- Updated sender assignment logic
- Updated statistics logging to show "BSRI Team" instead of "Events Team"

#### `aug_generate_embeddings.py`
- Updated statistics to show both "BSRI Team" and legacy "Events Team" counts
- Maintains backward compatibility with existing data

### 4. New Test Files Created

#### `test_sender_logic.py`
- Comprehensive test suite for the new sender determination logic
- Tests various email header formats
- Validates both BSRI Team and Guest classifications

#### `migrate_sender_data.py`
- Migration script to update existing data
- Can run in dry-run mode to preview changes
- Updates both original emails and embeddings collections
- Maintains data integrity during migration

## Email Header Formats Supported

The new logic handles various email header formats:

✅ **BSRI Team Examples:**
- `Events Team <events@bigsurriverinn.com>`
- `events@bigsurriverinn.com`
- `John Doe <john@bigsurriverinn.com>`
- `EVENTS@BIGSURRIVERINN.COM` (case insensitive)
- `Big Sur River Inn <info@bigsurriverinn.com>`

✅ **Guest Examples:**
- `john.doe@gmail.com`
- `Jane Smith <jane@example.com>`
- `Events Team <events@otherdomain.com>`
- `customer@yahoo.com`

## Benefits

1. **Domain-based Classification:** More reliable than text matching
2. **Case Insensitive:** Handles various email formats
3. **Robust Parsing:** Extracts email addresses from complex headers
4. **Future Proof:** Any new @bigsurriverinn.com email will be correctly classified
5. **Backward Compatible:** Existing data can be migrated

## Usage

### Running the Updated Scripts
```bash
# Collect emails with new sender logic
python aug_collect_all_emails.py

# Update emails with new sender logic
python aug_update_emails.py

# Generate embeddings (will use updated sender data)
python aug_generate_embeddings.py
```

### Testing the Logic
```bash
# Test the sender determination logic
python test_sender_logic.py
```

### Migrating Existing Data
```bash
# Preview what would be changed (dry run)
python migrate_sender_data.py

# To actually perform migration, edit the file and uncomment:
# migrator.run_migration(dry_run=False)
```

## Database Impact

### Collections Affected
- `email_chatbot.original_emails`
- `email_chatbot.email_embeddings`

### Fields Updated
- `sender` field: "Events Team" → "BSRI Team" (where applicable)

### Statistics
The updated scripts will show:
- Guest messages: [count]
- BSRI Team messages: [count]
- Events Team (legacy): [count] (if any remain)

## Next Steps

1. **Test the updated logic** with your email data
2. **Run migration script** to update existing data
3. **Verify statistics** show correct sender distribution
4. **Update any downstream processes** that reference "Events Team" to use "BSRI Team"

## Rollback Plan

If needed, the migration can be reversed by:
1. Running a reverse migration script
2. Restoring from database backup
3. The old logic is preserved in git history
