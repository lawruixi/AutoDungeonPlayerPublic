import json
import matplotlib.pyplot as plt


def read_and_intepret(filename):
    input_file = open(filename,"r")
    cases = 0
    wins = 0
    moves = 0
    kills = 0
    win_health = 0
    for line in input_file:
        json_dict = json.loads(line.strip())
        if "Total stats" in json_dict:
            json_dict2 = json_dict

        else:
            if json_dict["Win_state"] == True:
                wins+=1
                win_health += int(json_dict["Health"])
            cases+=1
            moves+=int(json_dict["Turns"])
            kills+=int(json_dict["Kills"])
    json_dict2["Win Percentage"] = wins/cases
    json_dict2["Average Kills"] = kills/cases
    json_dict2["Average Number of Turns"] = moves/cases
    json_dict2["Average Health on Win"] = win_health/cases

    print("Cases: "+str(cases))
    print("Win percentage: "+str(wins/cases))
    print("Average moves: "+str(moves/cases))
    print("Average kills: "+str(kills/cases))
    print("Average health on win: "+str(win_health/cases))

    return json_dict

def read_and_graph(filenames,comparison_class_x,comparison_class_y):
    data = []
    for file in filenames:
        json_dict =  read_and_intepret(file)
        data.append((float(json_dict[comparison_class_x]),(float(json_dict[comparison_class_y]))))
        #datay.append(float(json_dict[comparison_class_y]))
    data.sort()
    datax,datay = [],[]
    for i in data:
        datax.append(i[0])
        datay.append(i[1])

    plt.plot(datax,datay)
    plt.xlabel(comparison_class_x)
    plt.ylabel(comparison_class_y)
    plt.show()

def read_and_graph_2(filenames,comparison_class_x,comparison_class_y, save_fig = None):
    data = []
    labeler = filenames[0].replace(".txt","").replace("_"," ")[0:-1].title()
    for file in filenames:
        json_dict =  read_and_intepret(file)
        data.append((float(json_dict[comparison_class_x]),(float(json_dict[comparison_class_y]))))
        #datay.append(float(json_dict[comparison_class_y]))
    data.sort()
    datax,datay = [],[]
    for i in data:
        datax.append(i[0])
        datay.append(i[1])

    plt.plot(datax,datay,marker="o",label = labeler)
    plt.legend()
    plt.xlabel(comparison_class_x)
    plt.ylabel(comparison_class_y)
    plt.ylim(0.0, 1.0)
    if save_fig != None:
        plt.savefig(save_fig,transparent = True)
    plt.show()



def read_and_graph_multi(list_of_filenames,comparison_class_x,comparison_class_y,save_fig = None):
    list_of_colors = ['m','c','g','r','b']
    list_of_markers = ['D''s','p','^','x','o']
    for filenames in list_of_filenames:
        data = []
        labeler = filenames[0].replace(".txt","").replace("_"," ")[0:-1].title()
        for file in filenames:
            json_dict =  read_and_intepret(file)
            data.append((float(json_dict[comparison_class_x]),(float(json_dict[comparison_class_y]))))
            #datay.append(float(json_dict[comparison_class_y]))
        data.sort()
        datax,datay = [],[]
        for i in data:
            datax.append(i[0])
            datay.append(i[1])

        plt.plot(datax,datay,marker=list_of_markers.pop(),color=list_of_colors.pop(),label = labeler)
    plt.legend()
    plt.xlabel(comparison_class_x)
    plt.ylabel(comparison_class_y)
    plt.ylim(0.0, 1.0)
    if save_fig != None:
        plt.savefig(save_fig)

    plt.show()


read_and_graph_multi([["swarm_defensive_test_enemy_count_1.txt","swarm_defensive_test_enemy_count_2.txt", "swarm_defensive_test_enemy_count_3.txt"
,"swarm_defensive_test_enemy_count_4.txt","swarm_defensive_test_enemy_count_5.txt", "swarm_defensive_test_enemy_count_6.txt"],
["swarm_more_defensive_test_enemy_count_1.txt","swarm_more_defensive_test_enemy_count_2.txt", "swarm_more_defensive_test_enemy_count_3.txt"
,"swarm_more_defensive_test_enemy_count_4.txt","swarm_more_defensive_test_enemy_count_5.txt", "swarm_more_defensive_test_enemy_count_6.txt"],
["swarm_offensive_test_enemy_count_1.txt","swarm_offensive_test_enemy_count_2.txt", "swarm_offensive_test_enemy_count_3.txt"
,"swarm_offensive_test_enemy_count_4.txt","swarm_offensive_test_enemy_count_5.txt", "swarm_offensive_test_enemy_count_6.txt"]]
,"Enemy Count","Win Percentage","Second Trial Graph.png")