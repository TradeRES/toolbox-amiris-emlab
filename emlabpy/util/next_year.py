
def update_years_file(current_year , lookAhead, final_year):
    fieldnames = ['current', 'future', "final"]
    print("updated years file")
    #TODO dont hard code the path, once the spine bug is fixed. then it can be exported to the output folder.
    # the clock is executed in the util folder. So save the results in the parent folder: emlabpy
    complete_path =  os.path.join(os.path.dirname(os.getcwd()),  globalNames.years_path)
    with open(complete_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter ='/')
        csvwriter.writerow([current_year, (current_year + lookAhead), final_year])