import os
from typing import Dict, List, Union

import matplotlib.pyplot as plt
import numpy as np
from commonroad.planning.planning_problem import PlanningProblemSet
from commonroad.prediction.prediction import TrajectoryPrediction
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleType
from commonroad.scenario.scenario import Scenario
from commonroad.visualization.draw_params import MPDrawParams
from commonroad.visualization.mp_renderer import MPRenderer
from matplotlib.animation import FuncAnimation


def get_final_time_step_in_scenario(scenario: Scenario):
    final_time_steps = []
    for obstacle in scenario.obstacles:
        if isinstance(obstacle, DynamicObstacle):
            if obstacle.prediction is not None:
                final_time_steps.append(obstacle.prediction.final_time_step)
            else:
                final_time_steps.append(obstacle.initial_state.time_step)

    return max(final_time_steps)


def create_video(
    scenario: Scenario,
    output_folder: str,
    planning_problem_set: PlanningProblemSet = None,
    trajectory_pred: Union[
        Dict[int, DynamicObstacle], List[TrajectoryPrediction]
    ] = None,
    follow_ego: bool = False,
    suffix: str = "",
    file_type: str = "mp4",
) -> str:
    """
    Create video for a simulated scenario and the list of ego vehicles.

    :param scenario: Final commonroad scenario
    :param output_folder: path to output folder
    :param planning_problem_set: possibility to plot a Commonroad planning problem
    :param trajectory_pred: list of one or more ego vehicles or their trajectory predictions
    :param follow_ego: focus video on the ego vehicle(s)
    :param suffix: possibility to add suffix to file name
    :param file_type: mp4 or gif files supported
    :return:
    """
    assert file_type in ("mp4", "gif")

    # add short padding to create a short break before the loop (1sec)
    frame_count_padding = int(1 / scenario.dt)
    frame_count = get_final_time_step_in_scenario(scenario) + frame_count_padding
    dynamic_obstacles_ego = []
    if trajectory_pred is None:
        trajectory_pred = []

    if len(trajectory_pred) > 0 and isinstance(
        list(trajectory_pred.values())[0], DynamicObstacle
    ):
        trajectories_tmp = []

        for ego_vehicle in trajectory_pred.values():
            dynamic_obstacles_ego.append(ego_vehicle)
            trajectories_tmp.append(ego_vehicle.prediction)
        trajectory_pred = trajectories_tmp

    for prediction in trajectory_pred:
        frame_count = len(prediction.trajectory.state_list) + frame_count_padding
        # create the ego vehicle prediction using the trajectory and the shape of the obstacle
        dynamic_obstacle_initial_state = prediction.trajectory.state_list[0]

        # generate the dynamic obstacle according to the specification
        dynamic_obstacle_id = scenario.generate_object_id()
        dynamic_obstacle_type = ObstacleType.CAR
        ego_dynamic_obstacle = DynamicObstacle(
            dynamic_obstacle_id,
            dynamic_obstacle_type,
            prediction.shape,
            dynamic_obstacle_initial_state,
            prediction,
        )
        dynamic_obstacles_ego.append(ego_dynamic_obstacle)

    if follow_ego:
        if trajectory_pred:
            # a dictionary that holds the plot limits at each time step
            dict_plot_limits = get_dynamic_plot_limits(trajectory_pred, frame_count)
        else:
            # warnings.warn("Unable to follow the ego vehicle as no trajectory is provided!")
            dict_plot_limits = get_plot_limits(scenario, frame_count)
    else:
        dict_plot_limits = get_plot_limits(scenario, frame_count)

    interval = (
        1000 * scenario.dt
    )  # delay between frames in milliseconds, 1 second * dt to get actual time in ms

    dpi = 150
    figsize = (5, 5)
    draw_params = MPDrawParams()
    draw_params.axis_visible = False
    rnd = MPRenderer(figsize=figsize, draw_params=draw_params)
    rnd.ax.axes.get_xaxis().set_visible(False)
    (ln,) = plt.plot([], [], animated=True)

    def init_plot():
        plt.cla()
        if planning_problem_set is not None:
            planning_problem_set.draw(rnd)

        if dynamic_obstacles_ego is not None:
            draw_params = MPDrawParams()
            draw_params.time_begin = 0
            draw_params.time_end = 0
            draw_params.axis_visible = False
            draw_params.dynamic_obstacle.vehicle_shape.occupancy.shape.facecolor = (
                "green"
            )
            rnd.draw_list(dynamic_obstacles_ego, draw_params)

        draw_params = MPDrawParams()
        draw_params.time_begin = 0
        draw_params.time_end = 0
        scenario.draw(renderer=rnd, draw_params=draw_params)
        rnd.plot_limits = dict_plot_limits[0]
        rnd.render()
        plt.draw()
        rnd.f.tight_layout()
        return (ln,)

    def animate_plot(frame):
        rnd.clear(keep_static_artists=False)
        if planning_problem_set is not None:
            planning_problem_set.draw(rnd)

        draw_params = MPDrawParams()
        draw_params.time_begin = frame
        draw_params.time_end = frame
        rnd.draw_list(scenario.dynamic_obstacles, draw_params=draw_params)

        if dynamic_obstacles_ego is not None:
            draw_params = MPDrawParams()
            draw_params.time_begin = frame
            draw_params.time_end = frame
            draw_params.dynamic_obstacle.vehicle_shape.occupancy.shape.facecolor = (
                "green"
            )
            rnd.draw_list(dynamic_obstacles_ego, draw_params=draw_params)

        draw_params = MPDrawParams()
        draw_params.time_begin = 0
        draw_params.time_end = 0
        scenario.lanelet_network.draw(renderer=rnd, draw_params=draw_params)

        rnd.plot_limits = dict_plot_limits[frame]
        rnd.f.tight_layout()
        rnd.render()
        return (ln,)

    anim = FuncAnimation(
        rnd.f,
        animate_plot,
        frames=frame_count,
        init_func=init_plot,
        blit=True,
        interval=interval,
    )

    file_name = str(scenario.scenario_id) + suffix + os.extsep + file_type
    anim.save(os.path.join(output_folder, file_name), dpi=dpi, writer="ffmpeg")
    plt.close(rnd.f)
    return file_name


def get_plot_limits(scenario: Scenario, frame_count):
    """
    The plot limits track the center of the ego vehicle.
    """

    def flatten(list_to_flat):
        return [item for sublist in list_to_flat for item in sublist]

    center_vertices = np.array(
        flatten(
            [lanelet.center_vertices for lanelet in scenario.lanelet_network.lanelets]
        )
    )

    min_coords = np.min(center_vertices, axis=0)
    max_coords = np.max(center_vertices, axis=0)
    dict_plot_limits = [
        [min_coords[0], max_coords[0], min_coords[1], max_coords[1]]
    ] * frame_count

    return dict_plot_limits


def get_dynamic_plot_limits(
    predictionss: List[TrajectoryPrediction], frame_count, area_size=120
):
    """
    The plot limits track the center of the ego vehicles.
    """
    num_time_step_trajectories_max = max(
        [len(prediction.trajectory.state_list) for prediction in predictionss]
    )

    dict_plot_limits = list()
    for i in range(frame_count):
        if i < num_time_step_trajectories_max:
            list_states_vehicles = get_state_list_of_trajectories(i, predictionss)
        else:
            list_states_vehicles = get_state_list_of_trajectories(
                num_time_step_trajectories_max - 1, predictionss
            )

        x_min = min([state.position[0] for state in list_states_vehicles]) - area_size
        x_max = max([state.position[0] for state in list_states_vehicles]) + area_size
        y_min = min([state.position[1] for state in list_states_vehicles]) - area_size
        y_max = max([state.position[1] for state in list_states_vehicles]) + area_size

        dict_plot_limits.append([x_min, x_max, y_min, y_max])

    return dict_plot_limits


def get_state_list_of_trajectories(
    time_step: int, trajectories: List[TrajectoryPrediction]
):
    """
    Returns the list of states of trajectories at the specified time step.
    """
    list_states = []
    for trajectory in trajectories:
        try:
            list_states.append(trajectory.trajectory.state_list[time_step])
        except IndexError:
            pass

    return list_states
