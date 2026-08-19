

def get_temperature(city: str):
    print(f'\n\nGET TEMPARATURE: {city}\n\n\n')
    if city == 'London':
        return '17 degrees'
    elif city == 'Budapes':
        return '30 degrees'
    else:
        return 'it is literally impossible to determine temparature for this city'