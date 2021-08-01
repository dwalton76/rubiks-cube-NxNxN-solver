# standard libraries
import logging

# third party libraries
import click

# rubiks cube libraries
from rubikscubennnsolver import configure_logging
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--cube-count", type=int, default=10, show_default=True, help="number of cubes to scramble")
@click.option("--move-count", type=int, default=15, show_default=True, help="number of moves for scrambling")
@click.option("--batch-size", type=int, default=100, show_default=True, help="how often to write to disk")
@click.option("--filename", type=str, default="cube.csv", show_default=True, help="ressults filename")
def stage_centers_555(cube_count: int, move_count: int, batch_size: int, filename: str) -> None:
    cube = RubiksCube555(solved_555, "URFDLB")
    cube.cpu_mode = "normal"
    cube.lt_init()
    cube.re_init()
    original_state = cube.state[:]

    with open(filename, "w") as fh_nn:  # noqa: F841
        # fh_nn.write(",".join([f"PT{x}" for x in range(pt_count)]))
        # fh_nn.write(",COST\n")

        # scramble CUBE_COUNT cubes up to MOVE_COUNT random moves
        for x in range(cube_count):
            cube.state = original_state[:]

            for y in range(move_count):
                cube.randomize(count=1)

            cube.print_cube()


@cli.command()
def lr_centers_555() -> None:
    filename_nn = "cube.csv"
    cube = RubiksCube555(solved_555, "URFDLB")
    cube.cpu_mode = "normal"
    cube.lt_init()
    cube.re_init()
    pt_count = len(cube.lt_LR_centers_stage.prune_tables)

    BATCH_SIZE = 10
    to_write = []
    to_write_count = 0
    original_state = cube.state[:]

    with open(filename_nn, "w") as fh_nn:
        fh_nn.write(",".join([f"PT{x}" for x in range(pt_count)]))
        fh_nn.write(",COST\n")

        # solve 10000 random cubes
        for x in range(10000):
            cube.state = original_state[:]
            cube.randomize()
            cube.solution = []

            cube.lt_LR_centers_stage.solve_via_c()
            logger.info(cube.solve_via_c_output)
            in_table = False

            for line in cube.solve_via_c_output.splitlines():
                if line.startswith("       ===  ===  ===  ===  ==="):
                    in_table = True

                elif in_table:
                    if line:
                        line = line.strip().split()
                        cost_to_goal = line[-2]

                        if cost_to_goal != "0":
                            nn_line = line[1 : pt_count + 1]
                            nn_line.append(cost_to_goal)
                            to_write.append(",".join(nn_line))
                            to_write_count += 1

                    else:
                        in_table = False
                        break

            if to_write_count >= BATCH_SIZE:
                fh_nn.write("\n".join(to_write) + "\n")
                fh_nn.flush()
                to_write = []
                to_write_count = 0

        if to_write_count:
            fh_nn.write("\n".join(to_write) + "\n")
            fh_nn.flush()
            to_write = []
            to_write_count = 0


if __name__ == "__main__":
    configure_logging()
    cli()
