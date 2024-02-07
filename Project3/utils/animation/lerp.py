import glm

class BezierInterpolate():
    @staticmethod
    def cubic_bezier(ax, ay, bx, by, t):
        x = 3 * pow(1 - t, 2) * t * ax + 3 * (1 - t) * pow(t, 2) * bx + pow(t, 3)
        y = 3 * pow(1 - t, 2) * t * ay + 3 * (1 - t) * pow(t, 2) * by + pow(t, 3)
        
        return x, y