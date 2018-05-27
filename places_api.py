import pip
import pandas
import requests
import argparse
import platform
import os
import datetime
from pandas import DataFrame
import numpy as np

plat=platform.system()
if plat == 'Linux':
    clear_message='clear'
else:
    clear_message='cls'

Methods = ['A', 'B', 'C', 'D','E']

def openfile(filename):
    # Load spreadsheet
    xl = pandas.ExcelFile(filename)
    # totlen = len(xl.parse)
    # Load a sheet into a DataFrame by name: df1
    return xl.parse()

def openfileadv(filename,Srows=0,Nrows=10):  
    xl = pandas.ExcelFile(filename)
    x = xl.parse(skiprows=Srows,nrows=Nrows)
    return x


def totlines(filename):
    xl = pandas.ExcelFile(filename)
    totlen = len(xl.parse())
    return totlen


def concat(row, index_dep=0, index_end=2, index_var = 2):
    # row is a numpy array
    resultant_row = row[index_dep:index_end]
    resultant_row.append(row[index_var])
    return ' '.join(resultant_row)

def clean_row(row):
    row_as_list = row.tolist()
    for col in row_as_list:
        if type(col) == float:
            row_as_list.remove(col)
    return row_as_list



def request_api(base_url, input_data):
    return requests.get(base_url, params=input_data).json()
    

def format_output(json_data):
    try:
        result = json_data["result"]
    except KeyError:
        result = dict()

    try:
        types = result["types"]
        if 'point_of_interest' in types:
            types.remove('point_of_interest')
        if 'establishment' in types:
            types.remove('establishment')
    except KeyError:
        types = ' '
    try:
        website = result["website"] 
    except KeyError: 
        website = ' '

    try:
        name = result["name"]
    except KeyError:
        name = ' '

    try:
        formatted_address = result["formatted_address"]
    except KeyError:
        formatted_address = ' '

    try:
        international_phone_number = result["international_phone_number"]
    except KeyError:
        international_phone_number = ' '

    try:
        reviews = len(result["reviews"])
    except KeyError:
        reviews = ' '

    try:
        rating = result["rating"]
    except KeyError:
        rating = ' '

    try:
        lat = result["geometry"]["location"]["lat"]
    except KeyError:
        lat = ' '

    try:
        lng = result["geometry"]["location"]["lng"]
    except KeyError:
        lng = ' '

    try:
        p_id = result["place_id"]
    except KeyError:
        p_id = ' '

    data = {
        "google name": name,
        "types": types,
        "website": website,
        "formatted address": formatted_address,
        "international phone number": international_phone_number,
        "total reviews": reviews,
        "rating": rating,
        "location Latitude": lat,
        "location Longitude": lng,
        "google place id": p_id,
        "status code": json_data["status"]
    }
    return data


def get_place_id(base_url,key,data):
    global clear_message
    place_ids = list()
    j = 0
    for row in data:
        #os.system(clear_message)
        # clnrow = clean_row(row)
        clnrow = row.tolist()
        for col in clnrow:
            if type(col) == float:
                clnrow.remove(col)
        rowlen = len(clnrow)
        print(clnrow)
        place_id = 'ZERO_RESULTS'
        for i in range(2,rowlen):
            print clnrow[i]
            if clnrow[i] != ' ':
                print('Method ' + Methods[(i-2)])
                input_data = {'input': concat(clnrow,index_var=i),'types' : 'establishment','key': key, 'language':'en'}
                #i should see all A-D but not
                print(input_data)
                res = request_api(base_url, input_data)
                pred = res["predictions"]
                
                # if res['status']:
                #     exit()

                
                if len(pred)>0:
                    place_id = pred[0]["place_id"]
                    break
                # else:
                #     place_id = 'ZERO_RESULTS'
                print(place_id)
                
          
        if place_id == 'ZERO_RESULTS':
            print clnrow[i]
            for i in range(2,rowlen):
                if clnrow[i] != ' ': 
                    print ('Method E (' + Methods[(i-2)] + ')')  
                    place_id = force_get_place_id(base_url, key, clnrow, i)
                    print(place_id)
                    if place_id != 'ZERO_RESULTS':
                        break



        place_ids.append(place_id) 
        print(res)    
        j += 1
    return place_ids


def force_get_place_id(base_url, key, row, ind_var):

    first_query = {
        'input': concat(row, index_dep=1,index_end=2,index_var=ind_var),
        'types': '(regions)', 
        'key': key,
        'language': 'en'
        }
    print(first_query)
    first_query_res = request_api(base_url, first_query)

    if first_query_res["status"] == 'OK':
        area_p_id = first_query_res["predictions"][0]["place_id"]
        second_url_base = 'https://maps.googleapis.com/maps/api/place/details/json?'
        second_query = {'placeid': area_p_id, 'key': key, 'language':'en'}
        second_query_res = request_api(second_url_base, second_query)

        if second_query_res["status"]=='OK':
            location = second_query_res["result"]["geometry"]["location"]
            final_query = {
                'location': "{},{}".format(location["lat"], location["lng"]),
                'radius':50000,
                'keyword': concat(row,index_dep=0,index_end=0,index_var=0),
                'types' : 'establishment',
                'key': key,
                'language':'en'
                }
            print(final_query)
            final_url_base = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
            final_query_res = request_api(final_url_base, final_query)

            if final_query_res["status"]=='OK':
                place_id = final_query_res["results"][0]["place_id"]
            else:
                place_id = 'ZERO_RESULTS'
        else:
            place_id = 'ZERO_RESULTS'
    else:
        place_id = 'ZERO_RESULTS'
    return place_id



def get_place_details(base_url, key, place_ids):
    global clear_message
    final_data = list()
    i=1
    for id in place_ids:
        #os.system(clear_message)
        if id != 'ZERO_RESULTS':
            input_data = {'placeid': id, 'key': key}
            res = request_api(base_url, input_data)
        else:
            res = {"status":id}
        final_data.append(format_output(res))
        print(i)
        i+=1
    return final_data


def to_spreadsheet(final_data,input_df,outputfile):
    df1 = pandas.DataFrame(final_data)
    df2 = pandas.concat([input_df, df1], axis=1)
    writer = pandas.ExcelWriter(outputfile)
    df2.to_excel(writer, 'Sheet1', index=False)
    df1.to_excel(writer, 'Sheet2')
    input_df.to_excel(writer, 'Sheet3')
    writer.save()


def setup_parser():
    """
    this methose setup the argparser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        required=True,
        help='input file.xlsx name if in same directory, path if in different directory',
        type=str
    )
    parser.add_argument(
        '--output',
        default='input',
        help='output file.xlsx name if in same directory, path if in different directory\ninput file by defaul',
        type=str
    )
    parser.add_argument(
        '--maxlines',
        default='10',
        help='maxlines to be read for a set',
        type=str
    )
    return parser


def main():
    parser = setup_parser()
    parsed = parser.parse_args()
    global clear_message
    os.system(clear_message)
    places_api_autocomplete = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?'
    places_api_details = 'https://maps.googleapis.com/maps/api/place/details/json?'
    key = 'AIzaSyAntcieEinaQ7sgryc3LyjZznbCj96KmaA'

    max_lines = int(parsed.maxlines)
    
    
    print(max_lines)
    input_file = parsed.input
    if parsed.output == 'input':
        outputFile = parsed.input
    else:
        outputFile = parsed.output   


    # input_df = openfile(input_file,max_lines)
    TotLines = totlines(filename=input_file)
    if max_lines > TotLines:
        max_lines = TotLines
    
    print(TotLines)
    SplitData = TotLines//max_lines
    print(SplitData)
    lastDataSet = TotLines%max_lines
    input_df = openfile(filename=input_file)
    # input_df.drop(['Score'], axis=1, inplace=True)
    
    for i in range(0,SplitData):
        output_file = outputFile  
        # in_df = openfileadv(filename=input_file,Srows=i*(max_lines),Nrows=max_lines)
        df = DataFrame(input_df[(i*max_lines):((i+1)*max_lines)])
        df = df.replace(np.nan, ' ', regex=True)
        df.index = range(len(df))
        data = df[['name', 'country', 'region', 'city', 'district','booking location']].values
        place_ids=get_place_id(places_api_autocomplete,key,data)
        os.system(clear_message)
        print('step 1 Done!')
        final_data = get_place_details(places_api_details, key, place_ids)
        os.system(clear_message)
        print('step 2 Done!')
        d = datetime.datetime.now().strftime('%A_%d_%B_%H%M%S_%Y')
        output_file = output_file.replace('.xlsx','')
        output_file = output_file + '_' + str(i*max_lines + 1) + '_' + str((i+1)*max_lines)+d+'.xlsx'
        # df = df.drop(df.columns[0],axis=1,inplace=True)
        to_spreadsheet(final_data,df,output_file)
        os.system(clear_message)
        print('Done!')

    if lastDataSet != 0:
        output_file = outputFile  
        df = DataFrame(input_df[(SplitData*max_lines):TotLines])
        df = df.replace(np.nan, ' ', regex=True)
        df.index = range(len(df))
        data = df[['name', 'country', 'region', 'city', 'district','booking location']].values
        place_ids=get_place_id(places_api_autocomplete,key,data)
        os.system(clear_message)
        print('step 1 Done!')
        final_data = get_place_details(places_api_details, key, place_ids)
        os.system(clear_message)
        print('step 2 Done!')
        d = datetime.datetime.now().strftime('%A_%d_%B_%H%M%S_%Y')
        output_file = output_file.replace('.xlsx','')
        output_file = output_file + '_' + str(SplitData*max_lines + 1) + '_' + str(SplitData*max_lines+lastDataSet)+d+'.xlsx'
        to_spreadsheet(final_data,df,output_file)
        os.system(clear_message)
        print('Done!')
    

if __name__=='__main__':
    main()
