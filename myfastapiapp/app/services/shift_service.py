import json
import random
from datetime import datetime, timedelta
from ..dependencies.database_connector import DBConnector
import logging

logging.basicConfig(level=logging.DEBUG)

async def generate_shifts():
    # Set the start and end dates for fetching data
    start_date = datetime(2024, 8, 12)
    end_date = datetime(2024, 9, 15)

    # Fetch the forecast data and staff data from MongoDB
    forecast_data = await DBConnector.fetch_forecast_for_shift(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    staff_data = await DBConnector.fetch_all_staff_for_shift()

    # Logging fetched data
    logging.debug(f"Forecast Data: {forecast_data}")
    logging.debug(f"Staff Data: {staff_data}")

    # Generate shifts with the new logic
    shifts = assign_six_hour_shifts_with_weekly_reset(forecast_data, staff_data)

    # Format the shifts and remove duplicates before saving
    structured_shifts = remove_duplicates_and_combine_shifts_mongodb(shifts)

    # Save the generated shifts back to the database, excluding `_id` since MongoDB auto-generates it
    for shift in structured_shifts:
        shift.pop('_id', None)

    await DBConnector.save_shifts(structured_shifts)

    logging.debug(f"Structured Shifts: {structured_shifts}")
    return {"message": "Shifts generated successfully", "shifts": structured_shifts}

def reset_available_hours_weekly(staff_data):
    for staff in staff_data:
        staff['user_data']['available_hours'] = 40  # Assuming 40 hours available per week

def assign_six_hour_shifts_with_weekly_reset(forecast_data, staff_data):
    schedule = []
    current_week = None

    for forecast in forecast_data:
        date = forecast["date"]
        week_of_year = datetime.strptime(date, '%Y-%m-%d').isocalendar()[1]
        
        # Reset available hours at the start of each week
        if week_of_year != current_week:
            reset_available_hours_weekly(staff_data)
            current_week = week_of_year

        staff_needed = forecast["staff_needed"]
        total_shifts_needed = staff_needed * 2  # Each staff is split into 2 shifts (opening and closing)

        available_staff = staff_data.copy()
        random.shuffle(available_staff)

        assigned_staff = []

        # Assign 6-hour shifts: Half for opening, half for closing
        for i in range(total_shifts_needed):
            if available_staff:
                staff = available_staff.pop(0)
                # Check if the staff has enough available hours for a 6-hour shift
                if staff['user_data']['available_hours'] >= 6:
                    shift_type = 'opening' if i < (total_shifts_needed // 2) else 'closing'
                    shift_time = SHIFT_HOURS[shift_type]
                    staff['user_data']['available_hours'] -= 6
                    assigned_staff.append({
                        "username": staff["username"],
                        "email": staff["email"],
                        "role": staff["user_data"]["roles"][0],
                        "shift": [create_shift_entry(date, shift_time[0], shift_time[1])]
                    })

        schedule.extend(assigned_staff)

    return schedule

def remove_duplicates_and_combine_shifts_mongodb(schedule):
    combined_schedule = {}

    for entry in schedule:
        email = entry["email"]
        if email not in combined_schedule:
            combined_schedule[email] = {
                "username": entry["username"],
                "email": entry["email"],
                "role": entry["role"],
                "shift": entry["shift"]
            }
        else:
            combined_schedule[email]["shift"].extend(entry["shift"])

    # Convert back to a list for final output
    final_schedule = list(combined_schedule.values())

    return final_schedule

def create_shift_entry(date, start_time, end_time):
    return {
        "date": date,
        "time": f"{start_time} - {end_time}"
    }

SHIFT_HOURS = {
    'whole_day': ('09:00', '21:00'),
    'opening': ('09:00', '15:00'),
    'closing': ('15:00', '21:00'),
    'sunday': ('09:00', '17:00')
}
