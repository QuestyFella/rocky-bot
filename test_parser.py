import re

def parse_message(content):
    # Case-insensitive matching for field names using regex
    pattern = r"(?i)^Reason:\s*(.*?)\s*^Amount:\s*(.*?)\s*^Deadline:\s*(.*?)\s*^Note:\s*(.*)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    
    if not match:
        # Try to identify what might be wrong with the message
        lines = content.strip().split('\n')
        if len(lines) < 4:
            return {"error": "Message must contain at least 4 lines for Reason, Amount, Deadline, and Note."}
            
        # Check for case-insensitive field presence
        content_lower = content.lower()
        required_fields = ["reason", "amount", "deadline", "note"]
        missing_fields = [field for field in required_fields if field not in content_lower]
        
        if missing_fields:
            return {"error": f"Missing required fields: {', '.join(missing_fields)}"}
            
        return {"error": "Invalid format. Fields must be in the correct order."}
        
    reason, amount, deadline, note = match.groups()
    return {
        "Reason": reason.strip(),
        "Amount": amount.strip(),
        "Deadline": deadline.strip(),
        "Note": note.strip(),
    }

# Test cases
test_cases = [
    # Valid case
    """Reason: Test reason
Amount: 100
Deadline: 2023-12-31
Note: Test note""",
    
    # Valid case with different cases
    """reason: Test reason
amount: 100
deadline: 2023-12-31
note: Test note""",
    
    # Invalid case - missing field
    """Reason: Test reason
Amount: 100
Deadline: 2023-12-31""",
    
    # Invalid case - wrong order
    """Amount: 100
Reason: Test reason
Deadline: 2023-12-31
Note: Test note""",
    
    # Invalid case - too few lines
    """Reason: Test reason
Amount: 100"""
]

for i, test_case in enumerate(test_cases):
    print(f"Test case {i+1}:")
    result = parse_message(test_case)
    print(result)
    print()