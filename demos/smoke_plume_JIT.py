""" Smoke Plume
Hot smoke is emitted from a circular region at the bottom.
The simulation computes the resulting air flow in a closed box.
"""
from phi.torch.flow import *

TORCH.set_default_device('GPU')
math.set_global_precision(32)

DOMAIN = dict(x=128, y=128, bounds=Box[0:100, 0:100])
velocity = StaggeredGrid((0, 0), extrapolation.ZERO, **DOMAIN)  # or use CenteredGrid
smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=200, y=200, bounds=DOMAIN['bounds'])
INFLOW = 0.2 * CenteredGrid(SoftGeometryMask(Sphere(center=(50, 10), radius=5)), extrapolation.ZERO, resolution=smoke.resolution, bounds=smoke.bounds)
pressure = CenteredGrid(0, extrapolation.BOUNDARY, **DOMAIN)


@math.jit_compile
def step(smoke, velocity, pressure):
    smoke = advect.mac_cormack(smoke, velocity, 1) + INFLOW
    buoyancy_force = smoke * (0, 0.1) @ velocity  # resamples smoke to velocity sample points
    velocity = advect.semi_lagrangian(velocity, velocity, 1) + buoyancy_force
    with math.SolveTape() as tape:
        velocity, pressure = fluid.make_incompressible(velocity, (), Solve('CG', 1e-5, 0, x0=pressure))
    return smoke, velocity, pressure, tape.solves[0].iterations


viewer = view(smoke, velocity, 'pressure', play=True, scene=True, namespace=globals())
for i in viewer.range(warmup=1, range=100):
    print(f'Step number {i}')
    smoke, velocity, pressure, iterations = step(smoke, velocity, pressure)
    viewer.log_scalars(iterations=iterations)
