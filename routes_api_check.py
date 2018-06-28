import urllib.request, json
from bs4 import BeautifulSoup
from nltk import word_tokenize
from time import sleep

def mutual(start_destin,path_to):
    # Google MapsDdirections API endpoint
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    api_key = 'API KEY'
    # Asks the user to input Where they are and where they want to go.
    origin = start_destin.replace(' ', '+')
    destination = path_to.replace(' ', '+')
    print(origin)
    print(destination)
    # Building the URL for the request
    nav_request = 'origin={}&destination={}&key={}'.format(origin, destination, api_key)
    request = endpoint + nav_request
    # Sends the request and reads the response.
    response = urllib.request.urlopen(request).read()
    # Loads response as JSON
    directions = json.loads(response)
    routes = directions['routes']
    legs = routes[0]['legs']
    print(len(legs))
    first_step = legs[0]['steps']
    print(len(first_step))

    for i in range(0, len(first_step)):
        instructions = first_step[i]['html_instructions']
        distance = first_step[i]['distance']['text']
        soup = BeautifulSoup(instructions, "html5lib")
        go_direction = soup.get_text()
        print('Step no.' + str(i + 1) + ' : ')
        print(go_direction)
        conversion = distance.split(' ')
        if conversion[1] == 'km':
            org_distance = float(conversion[0]) * 1000
        if conversion[1] == 'm':
            org_distance = int(conversion[0])

        collector = word_tokenize(go_direction)
        # if int(distance) <
        print(distance)
        print(int(org_distance))

        if org_distance < 6:
            i = i + 1

        main_way_list = go_direction.split('(')
        main_way = main_way_list[0]

        directions = ['north', 'northeast', 'northwest', 'straight', 'left', 'right']

        goway = []

        for d in collector:
            for e in directions:
                if d.lower() == e:
                    goway.append(d)
        if len(goway) > 0:
            toggle_direction = goway[0]
            print(toggle_direction)




def location_initiate(start_destin,path_to):
    # Google MapsDdirections API endpoint
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    api_key = 'API KEY'
    destination = path_to.replace(' ', '+')

    while True:


        # Asks the user to input Where they are and where they want to go.
        origin = start_destin.replace(' ', '+')
        print(origin)
        print(destination)
        # Building the URL for the request
        nav_request = 'origin={}&destination={}&key={}'.format(origin, destination, api_key)
        request = endpoint + nav_request
        # Sends the request and reads the response.
        response = urllib.request.urlopen(request).read()
        # Loads response as JSON
        directions = json.loads(response)
        routes = directions['routes']
        legs = routes[0]['legs']
        #print(len(legs))
        first_step = legs[0]['steps']
        #print(len(first_step))
        instructions = first_step[0]['html_instructions']
        instructions_1 = first_step[1]['html_instructions']
        distance = first_step[0]['distance']['text']
        soup = BeautifulSoup(instructions, "html5lib")
        soup_1 = BeautifulSoup(instructions_1, "html5lib")
        go_direction_1 = soup.get_text()
        go_direction = soup.get_text()
        conversion = distance.split(' ')
        org_distance = 0
        if conversion[1] == 'km':
            org_distance = float(conversion[0]) * 1000
        if conversion[1] == 'm':
            org_distance = conversion[0]

        collector = word_tokenize(go_direction)
        #print(distance)
        #print(int(org_distance))

        main_way_list = go_direction.split('(')
        main_way = main_way_list[0]

        directions = ['north', 'northeast', 'northwest', 'straight', 'left', 'right']

        if int(org_distance) < 6:
            goway = []

            for d in collector:
                for e in directions:
                    if d.lower() == e:
                        goway.append(d)

            if len(goway) == 0:
                print(go_direction_1)
                print('turn in ' + str(org_distance) + ' m')

            else:
                toggle_direction = goway[1]
                print(toggle_direction)
                print('turn in ' + str(org_distance) + ' m')


        else:
            goway = []

            for d in collector:
                for e in directions:
                    if d.lower() == e:
                        goway.append(d)

            if len(goway) == 0:
                print(go_direction)
                print('straight')
                print('go on untill ' + str(org_distance) + ' metres')

            else:
                toggle_direction = goway[0]
                print(toggle_direction)
                print('straight')
                print('go on untill ' + str(org_distance) + ' metres')


        sleep(1)

def location_smart():
    from firebase import firebase
    # Google Maps Ddirections API endpoint
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    api_key = 'API KEY'
    firebase = firebase.FirebaseApplication('https://smartglass-e01ec.firebaseio.com/', None)

    while True:



            whole_direct = firebase.get('/directions', None)
            latt = whole_direct['latitude']
            long = whole_direct['longitude']
            latt_desti = whole_direct['desti_latitude']
            long_desti = whole_direct['desti_longitude']
            print(latt)
            print(long)
            destination = (str(latt_desti) + ', ' + str(long_desti))
            start_destin = (str(latt) + ', ' + str(long))
            # Asks the user to input Where they are and where they want to go.
            origin = start_destin.replace(' ', '+')
            destination = destination.replace(' ', '+')
            # Building the URL for the request
            nav_request = 'origin={}&destination={}&key={}'.format(origin, destination, api_key)
            request = endpoint + nav_request
            # Sends the request and reads the response.
            response = urllib.request.urlopen(request).read().decode('utf-8')
            # Loads response as JSON
            directions = json.loads(response)
            routes = directions['routes']
            legs = routes[0]['legs']
            # print(len(legs))
            first_step = legs[0]['steps']
            print(len(first_step))

            if len(first_step) > 1 :
                instructions_1 = first_step[1]['html_instructions']
                soup_1 = BeautifulSoup(instructions_1, "html5lib")
                go_direction_1 = soup_1.get_text()

            instructions = first_step[0]['html_instructions']
            distance = first_step[0]['distance']['text']
            soup = BeautifulSoup(instructions, "html5lib")
            go_direction = soup.get_text()
            conversion = distance.split(' ')
            org_distance = 0
            if conversion[1] == 'km':
                org_distance = float(conversion[0]) * 1000
            if conversion[1] == 'm':
                org_distance = conversion[0]

            collector = word_tokenize(go_direction)
            # print(distance)
            # print(int(org_distance))

            main_way_list = go_direction.split('(')
            main_way = main_way_list[0]

            directions = ['north', 'northeast', 'northwest', 'straight', 'left', 'right', 'south']

            if int(org_distance) < 10:
                goway = []

                for d in main_way:
                    for e in directions:
                        if d.lower() == e:
                            goway.append(d)

                if len(goway) == 0:
                    if len(first_step) > 1:
                        print(go_direction_1)
                    else:
                        print('go on you are on your last leg')
                    print('turn in ' + str(org_distance) + ' m')

                else:
                    if len(first_step) > 1:
                        toggle_direction = goway[1]
                        print(toggle_direction)
                    else:
                        print(toggle_direction)
                        print('go on you are on your last leg')
                    print('turn in ' + str(org_distance) + ' m')


            else:
                goway = []

                for d in main_way:
                    for e in directions:
                        if d.lower() == e:
                            goway.append(d)

                if len(goway) == 0:
                    print(go_direction)
                    print('straight')
                    print('go on untill ' + str(org_distance) + ' metres')

                else:
                    toggle_direction = goway[0]
                    if toggle_direction == 'south':
                        print('go back')
                    else:
                        print(toggle_direction)
                        print(go_direction)
                        print('straight')

                    print('go on untill ' + str(org_distance) + ' metres')


location_smart()


