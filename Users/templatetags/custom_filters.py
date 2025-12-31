from django import template


#These value|add:-1 are bulit-in filters


register = template.Library()

@register.filter
def get_val(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def days_since(value):
    """Extracts only the number of days from the timesince filter output."""
    timesince_str = value  # Expecting the output of timesince
    parts = timesince_str.split(",")  # Split by comma
    if "day" in parts[0]:  # Check if the first part contains "day"
        return parts[0] + " ago"
    return "Today"

@register.filter(name='success_rate_percentage')
def success_rate_percentage(question):
    """
    Custom filter to calculate the success rate of a question based on the success_rate field.
    It assumes that the 'success_rate' field is a dictionary with 'attempts' and 'correct' keys.
    Returns the percentage formatted to 2 decimal places.
    """
    if question.success_rate.get('attempts', 0) > 0:
        correct_attempts = question.success_rate.get('correct', 0)
        total_attempts = question.success_rate.get('attempts', 0)
        success_rate = (correct_attempts / total_attempts) * 100
        return f"{success_rate:.2f}"  # Format to 2 decimal places
    return "0.00"  # Return 0.00 if no attempts

@register.filter
def get_by_user(arg, user):
    """Returns the submission made by a specific user from the queryset, handling different user field names"""
    if not arg.exists():  # Avoid errors on empty QuerySet
        return None

   # model_name = arg.model.__name__  # Get the model name

    if hasattr(arg.model, "submitted_by"):  # Check if model has 'submitted_by' field
        return arg.filter(submitted_by=user).first()
    elif hasattr(arg.model, "user"):  # Check if model has 'user' field
        return arg.filter(user=user).first()
    
    return None  # Return None if neither field exists


@register.filter
def format_seconds(value):
    """
    Converts a time duration from seconds (float or int) into a human-readable format.

    - If the duration is less than 60 seconds, it shows only seconds (e.g., "8s").
    - If the duration is at least 1 minute, it shows minutes and optional seconds (e.g., "2m 5s").
    - If the duration is at least 1 hour, it includes hours, minutes, and optional seconds (e.g., "1h 2m 5s").
    - If the input is not a valid number or is negative, it returns "Invalid duration".

    Returns:
    str: Formatted duration string.

    """
    if not isinstance(value, (int, float)) or value < 0:
        return "Invalid duration"

    total_seconds = int(value)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_parts = []
    if hours:
        time_parts.append(f"{hours}h")
    if minutes:
        time_parts.append(f"{minutes}m")
    if seconds:
        time_parts.append(f"{seconds}s")

    return " ".join(time_parts) if time_parts else "0s"

@register.filter
def convert_duration(value):
    """
    Converts a duration field (timedelta) into a human-readable format (hours and minutes).
    """
    if not value:
        return "0 min"

    total_seconds = int(value.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if hours and minutes:
        return f"{hours}h {minutes}m"
    elif hours:
        return f"{hours}h"
    else:
        return f"{minutes}m"
    

@register.filter
def get_color_by_index(index):
    """
    Returns a Bootstrap button color class based on the index.
    Ensures safe integer conversion and cyclic color mapping.
    """
    colors = ["btn-primary", "btn-secondary", "btn-success",
              "btn-danger", "btn-warning", "btn-light", "btn-dark"]
    
    try:
        index = int(index)  
    except (ValueError, TypeError):
        return colors[0]  # Default color if index is invalid
    
    return colors[index % len(colors)]  # Cycle through colors 

@register.filter
def star_range(value):
    """Returns a range for iterating over a rating value (integer)."""
    try:
        return range(int(value))  # Ensure it's an integer
    except (ValueError, TypeError):
        return range(0)  # Default to zero if invalid

#not needed now 
@register.filter
def dict_key(dictionary, key):
    """Fetches the value for a key from a dictionary safely."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)  
    

@register.filter
def week_schedule(schedule):
    """
    Returns a list of dictionaries where each dictionary contains:
      - 'day': The name of the day (Monday - Sunday)
      - 'disabled': True if the schedule value is "None" or empty
      - 'btn_class': A Bootstrap button class based on the index
      {'day': 'Monday', 'disabled': False, 'btn_class': 'btn-primary'},
      {'day': 'Tuesday', 'disabled': True, 'btn_class': 'btn-secondary'},
    
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    btn_classes = ["btn-primary", "btn-secondary", "btn-success", "btn-danger", "btn-warning", "btn-light", "btn-dark"]

    result = []
    for i, day in enumerate(days): #enumerate have (0,Monday)
        value = schedule[i] if i < len(schedule) else None
        result.append({
            "day": day,
            "disabled": not value or value == "None",
            "btn_class": btn_classes[i]  # Assign button class based on index
        })
    #print(result)
    return result