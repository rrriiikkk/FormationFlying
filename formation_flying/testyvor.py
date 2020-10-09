import numpy as np
import matplotlib.pyplot as plt

selfpos = np.array([10,220])
selfdestination = np.array([213,19])
target_agentpos = np.array([35,180])
target_agentdestination = np.array([200,30])

def calcmiddlepoint(a, b):
    return [0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1])]

origin_midpoint = np.array(calcmiddlepoint(selfpos, target_agentpos))
dest_midpoint = np.array(calcmiddlepoint(selfdestination, target_agentdestination))

def distance_to_destination(origin, destination):
    return ((destination[0] - origin[0]) ** 2 + (destination[1] - origin[1]) ** 2) ** 0.5

def calc_joining_point(selfpos, selfdestination, target_agentpos, target_agentdestination):
    rotation = np.array([[0, -1], [1, 0]])

    origin_midpoint = np.array(calcmiddlepoint(selfpos, target_agentpos))
    dest_midpoint = np.array(calcmiddlepoint(selfdestination, target_agentdestination))

    trajectory_line = dest_midpoint - origin_midpoint
    trajectory_slope = (dest_midpoint[1]-origin_midpoint[1])/(dest_midpoint[0]-origin_midpoint[0])


    original_traject_agent1 = selfdestination - selfpos
    original_traject_agent2 = target_agentdestination - target_agentpos

    potential_joinpath_agent1 = origin_midpoint - selfpos
    potential_joinpath_agent2 = origin_midpoint - target_agentpos

    alpha_agent1 = np.dot(original_traject_agent1, potential_joinpath_agent1)
    alpha_agent2 = np.dot(original_traject_agent2, potential_joinpath_agent2)

    if alpha_agent1 < 0 and alpha_agent2 >= 0: # agent 1 is limiting factor
        distance = abs((np.cross(trajectory_line, potential_joinpath_agent1))/np.linalg.norm(trajectory_line))
        direction = (np.dot(rotation, trajectory_line))/np.linalg.norm(trajectory_line)
        if selfpos[1] > origin_midpoint[1]+trajectory_slope*(selfpos[0]-origin_midpoint[0]):
            joining_point = selfpos - direction*distance
        elif selfpos[1] < origin_midpoint[1]+trajectory_slope*(selfpos[0]-origin_midpoint[0]):
            joining_point = selfpos + direction*distance
        else:
            joining_point = selfpos

    elif alpha_agent1 >= 0 and alpha_agent2 < 0: # agent 2 is limiting factor
        distance = abs((np.cross(trajectory_line, potential_joinpath_agent2))/np.linalg.norm(trajectory_line))
        direction = (np.dot(rotation, trajectory_line))/np.linalg.norm(trajectory_line)
        if target_agentpos[1] > origin_midpoint[1]+trajectory_slope*(target_agentpos[0]-origin_midpoint[0]):
            joining_point = target_agentpos - direction*distance
        elif target_agentpos[1] < origin_midpoint[1]+trajectory_slope*(target_agentpos[0]-origin_midpoint[0]):
            joining_point = target_agentpos + direction*distance
        else:
            joining_point = target_agentpos

    elif alpha_agent1 >= 0 and alpha_agent2 >= 0:
        raise Exception("the origin midpoint cannot lay in front of both agents")

    return joining_point

def calc_leaving_point(selfpos, selfdestination, target_agentpos, target_agentdestination):

    rotation = np.array([[0, -1], [1, 0]])

    origin_midpoint = np.array(calcmiddlepoint(selfpos, target_agentpos))
    dest_midpoint = np.array(calcmiddlepoint(selfdestination, target_agentdestination))

    trajectory_line = dest_midpoint - origin_midpoint
    trajectory_slope = (dest_midpoint[1] - origin_midpoint[1]) / (dest_midpoint[0] - origin_midpoint[0])

    original_traject_agent1 = selfdestination - selfpos
    original_traject_agent2 = target_agentdestination - target_agentpos

    potential_leavepath_agent1 = selfdestination - dest_midpoint
    potential_leavepath_agent2 = target_agentdestination - dest_midpoint

    beta_agent1 = np.dot(original_traject_agent1, potential_leavepath_agent1)
    beta_agent2 = np.dot(original_traject_agent2, potential_leavepath_agent2)

    if beta_agent1 < 0 and beta_agent2 >= 0: # agent 1 is limiting factor
        distance = abs((np.cross(trajectory_line, potential_leavepath_agent1))/np.linalg.norm(trajectory_line))
        direction = (np.dot(rotation, trajectory_line))/np.linalg.norm(trajectory_line)
        if selfdestination[1] > dest_midpoint[1]+trajectory_slope*(selfdestination[0]-dest_midpoint[0]):
            leaving_point = selfdestination - direction * distance
        elif selfdestination[1] < dest_midpoint[1]+trajectory_slope*(selfdestination[0]-dest_midpoint[0]):
            leaving_point = selfdestination + direction * distance
        else:
            leaving_point = selfdestination

    elif beta_agent1 >= 0 and beta_agent2 < 0: # agent 2 is limiting factor
        distance = abs((np.cross(trajectory_line, potential_leavepath_agent2))/np.linalg.norm(trajectory_line))
        direction = (np.dot(rotation, trajectory_line))/np.linalg.norm(trajectory_line)
        if target_agentdestination[1] > dest_midpoint[1]+trajectory_slope*(target_agentdestination[0]-dest_midpoint[0]):
            leaving_point = target_agentdestination - direction * distance
        elif target_agentdestination[1] < dest_midpoint[1]+trajectory_slope*(target_agentdestination[0]-dest_midpoint[0]):
            leaving_point = target_agentdestination + direction * distance
        else:
            leaving_point = target_agentdestination

    elif beta_agent1 >= 0 and beta_agent2 >= 0:
        raise Exception("the origin midpoint cannot lay in front of both agents")
    else:
        raise Exception("the origin midpoint cannot lay behind both agents")

    return leaving_point

joining_point=calc_joining_point(selfpos,selfdestination,target_agentpos,target_agentdestination)
leaving_point=calc_leaving_point(selfpos,selfdestination,target_agentpos,target_agentdestination)

plt.scatter(selfpos[0],selfpos[1])
plt.scatter(selfdestination[0],selfdestination[1])
plt.scatter(target_agentpos[0],target_agentpos[1])
plt.scatter(target_agentdestination[0],target_agentdestination[1])
plt.scatter(joining_point[0],joining_point[1])
plt.scatter(leaving_point[0],leaving_point[1])
plt.plot([origin_midpoint[0],dest_midpoint[0]],[origin_midpoint[1],dest_midpoint[1]])
plt.axis('equal')

original_distance = distance_to_destination(selfdestination, selfpos) + distance_to_destination(target_agentpos, target_agentdestination)
agent1_distance = distance_to_destination(selfpos,joining_point)+0.75*distance_to_destination(joining_point,leaving_point)+distance_to_destination(leaving_point,selfdestination)
agent2_distance = distance_to_destination(target_agentpos,joining_point)+0.75*distance_to_destination(joining_point,leaving_point)+distance_to_destination(leaving_point,target_agentdestination)
fuel_savings = original_distance-agent1_distance-agent2_distance

plt.show()

