import math
import generate_triangles2

s3 = math.sqrt(3)

# T006 base coordinates (Hypotenuse BC on bottom)
pts_T006 = {
    \'A\': (3 * s3 / 2, 1.5),
    \'B\': (0, 0),
    \'C\': (2 * s3, 0)
}

# Generate 6a_C
generate_triangles2.draw(
    pts_T006,
    right_v=\'A\',
    side_labels={\'AB\': r\'$\', \'AC\': r\'$\sqrt{3}$\'},
    filename=\'tri2_T006_6a_C.png\',
    gap_factor=1.35
)
