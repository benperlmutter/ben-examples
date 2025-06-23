#!/usr/bin/env python3
"""
Test script for the new sender determination logic
"""
import re

def determine_sender(from_header: str) -> str:
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

def test_sender_logic():
    """Test various email header formats"""
    test_cases = [
        # BSRI Team cases
        ("Events Team <events@bigsurriverinn.com>", "BSRI Team"),
        ("events@bigsurriverinn.com", "BSRI Team"),
        ("John Doe <john@bigsurriverinn.com>", "BSRI Team"),
        ("EVENTS@BIGSURRIVERINN.COM", "BSRI Team"),
        ("Events Team <EVENTS@BIGSURRIVERINN.COM>", "BSRI Team"),
        ("Big Sur River Inn <info@bigsurriverinn.com>", "BSRI Team"),
        
        # Guest cases
        ("john.doe@gmail.com", "Guest"),
        ("Jane Smith <jane@example.com>", "Guest"),
        ("Events Team <events@otherdomain.com>", "Guest"),
        ("customer@yahoo.com", "Guest"),
        ("", "Guest"),
        ("Events", "Guest"),  # No email address
        ("Events Team", "Guest"),  # No email address
        
        # Edge cases
        ("Events Team <events@bigsurriverinn.com> via Gmail", "BSRI Team"),
        ("events+noreply@bigsurriverinn.com", "BSRI Team"),
        ("Events Team events@bigsurriverinn.com", "BSRI Team"),
    ]
    
    print("Testing sender determination logic...")
    print("=" * 60)
    
    all_passed = True
    for from_header, expected in test_cases:
        result = determine_sender(from_header)
        status = "✓" if result == expected else "✗"
        
        if result != expected:
            all_passed = False
        
        print(f"{status} '{from_header}' -> {result} (expected: {expected})")
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    test_sender_logic()
