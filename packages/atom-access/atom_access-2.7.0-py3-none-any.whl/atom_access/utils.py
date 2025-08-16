'''
This submodule contains utility functions
'''

import numpy.typing as npt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


def recursive_g(m: int) -> int:
    '''
    Recursively calculates numbers g_m required by ZCW
    algorithm

    Parameters
    ----------
    m : int
        m index

    Returns
    -------
    int
        g_m value for given m

    '''

    if m == 0:
        g = 8
    elif m == 1:
        g = 13
    else:
        g = recursive_g(m - 2) + recursive_g(m - 1)

    return g


def plot_rays(vecs: npt.NDArray, clusters: npt.NDArray, n_clust: int,
              show: bool = True, fig: go.Figure = None,
              colours: list[str] = None) -> None:
    '''
    Create a plot of unblocked rays for web browser using plotly

    Parameters
    ----------
    vecs : np.ndarray[float]
        (3,n_unblocked_rays) array containing xyz vectors of unblocked rays
    clusters : np.ndarray[int]
        Integers specifying which cluster each ray belongs to
    n_clust : int
        Number of clusters
    show : bool
        If true, displays figure in browser
    fig : go.Figure
        If provided, rays are added to this figure
    colours : list[str]
        List of colours, one per cluster formatted as\n
        [\n
            'rgb(VAL, VAL, VAL)',\n
            'rgb(VAL, VAL, VAL)',\n
            ...\n
        ]\n
        where VAL is Red, Green, Blue in range(0, 255)

    Returns
    -------
    go.Figure
        Figure of unblocked rays as points
    '''

    if not colours:
        colours = [
            'rgb(51 , 34 , 136)',
            'rgb(17 , 119, 51)',
            'rgb(68 , 170, 153)',
            'rgb(136, 204, 238)',
            'rgb(221, 204, 119)',
            'rgb(204, 102, 119)',
            'rgb(170, 68 , 153)',
            'rgb(136, 34 , 85)',
            'rgb(0  , 0  , 0)',
            'rgb(230, 159, 0)',
            'rgb(86 , 180, 233)',
            'rgb(0  , 158, 115)',
            'rgb(240, 228, 66)',
            'rgb(0  , 114, 178)',
            'rgb(213, 94 , 0)',
            'rgb(204, 121, 167)',
        ]

    if fig is None:
        fig = make_subplots()
    for cl in range(n_clust):
        # Unblocked rays
        fig.add_trace(
            go.Scatter3d(
                x=vecs[clusters == cl, 0],
                y=vecs[clusters == cl, 1],
                z=vecs[clusters == cl, 2],
                mode='markers',
                marker={'color': colours[cl]},
                showlegend=False
            )
        )

    # Turn off plotly gubbins
    layout = go.Layout(
        hovermode=False,
        dragmode='orbit',
        scene_aspectmode='cube',
        scene=dict(
            xaxis=dict(
                gridcolor='rgb(255, 255, 255)',
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=False,
                showgrid=False,
                zeroline=False,
                title='',
                showline=False,
                ticks='',
                showticklabels=False,
                backgroundcolor='rgb(255, 255,255)',
            ),
            yaxis=dict(
                gridcolor='rgb(255, 255, 255)',
                zerolinecolor='rgb(255, 255, 255)',
                showgrid=False,
                zeroline=False,
                title='',
                showline=False,
                ticks='',
                showticklabels=False,
                backgroundcolor='rgb(255, 255,255)',
            ),
            zaxis=dict(
                gridcolor='rgb(255, 255, 255)',
                zerolinecolor='rgb(255, 255, 255)',
                showgrid=False,
                title='',
                zeroline=False,
                showline=False,
                ticks='',
                showticklabels=False,
                backgroundcolor='rgb(255, 255,255)',
            ),
            aspectratio=dict(
                x=1,
                y=1,
                z=1
            ),
        ),
        margin={
            'l': 20,
            'r': 30,
            't': 30,
            'b': 20
        }
    )

    fig.update_layout(layout)

    if show:
        fig.show()

    return fig


def platform_check(func):
    '''
    Decorator to check platform for color terminal output.\n
    Windows Anaconda prompt will not support colors by default, so
    colors are disabled for all windows machines, unless the
    aa_term_color envvar is defined
    '''

    def check(*args):
        if 'nt' in os.name and not os.getenv('aa_term_color'):
            print(args[0])
        else:
            func(*args)

    return check


@platform_check
def cprint(string: str, color: str):
    '''
    Prints colored output to screen

    Parameters
    ----------
    string: str
        String to print
    color: str {red, green, yellow, blue, magenta, cyan, white}
        String name of color

    Returns
    -------
    None
    '''

    ccodes = {
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'yellow': '\u001b[33m',
        'blue': '\u001b[34m',
        'magenta': '\u001b[35m',
        'cyan': '\u001b[36m',
        'white': '\u001b[37m',
        'black_yellowbg': '\u001b[30;43m\u001b[K',
        'black_bluebg': '\u001b[30;44m\u001b[K',
    }
    end = '\033[0m\u001b[K'

    # Count newlines at neither beginning nor end
    num_c_nl = string.rstrip('\n').lstrip('\n').count('\n')

    # Remove right new lines to count left new lines
    num_l_nl = string.rstrip('\n').count('\n') - num_c_nl
    l_nl = ''.join(['\n'] * num_l_nl)

    # Remove left new lines to count right new lines
    num_r_nl = string.lstrip('\n').count('\n') - num_c_nl
    r_nl = ''.join(['\n'] * num_r_nl)

    # Remove left and right newlines, will add in again later
    _string = string.rstrip('\n').lstrip('\n')

    print('{}{}{}{}{}'.format(l_nl, ccodes[color], _string, end, r_nl))

    return
