Suppose you have a function on a product of intervals

We have some reason to believe that possibly after some coordinate change
the points that are some nice fraction of the way along each coordinate axis
are of more interest than the points where the coordinates do not have such nice form

Here nice form means that they are a/b^d with b something small like 2 or 3. b is fixed at the initial step

This means we are exploring points that are halfway or a third of the way along the interval
and then moving on to stepping by quarters or ninths and so on

The points we are exploring are grouped by the maximum power d when
each of the (before transformation) coordinates are
written as a/b^d in lowest terms, call this set of points G_d

### Decimation

If there are too many of these because the dimensionality of the box is large and/or
b^d is large, we can impose some decimation so only approximately f(d) many points are emitted
from G_d
if for a particular d, |G_d| <= f(d), this filtering does not take place
but because |G_d| grows so fast and the provided f(d) should have much slower growth
the filtering will happen at some stage
