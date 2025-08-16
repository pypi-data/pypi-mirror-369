import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.gaia import Gaia
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from IPython.display import display

class BrownDwarf(object):
    """Class for generating Brown Dwarf Objects

        This is a class for Brown Dwarf Objects

        Attributes:
        name (str): Name of object

        ra (float): RA, degrees

        dec (float) : Dec, degrees

        distance (float) : distance from, pc

        color (str, optional) : mpl supported color to plot object 

        temp (float, optional) : object temperature, K
    """


    def __init__(self, name, ra, dec, distance, color=False, temp = False):
        """Brown dwarf object

        This initializes a Brown Dwarf Object
        
        Args:
            name (str): Name of object

            ra (float): RA, degrees

            dec (float) : Dec, degrees

            distance (float) : distance from Sun, pc
            color (str, optional) : mpl supported color to plot object in

            temp (float, optional) : object temperature, K. 
                    Used to plot object color based on temp
        """
        self.name = name
        self.ra = ra * u.deg
        self.dec = dec * u.deg
        self.distance = distance * u.pc

        if color:
            self.color = color
        if temp:
            self.temp = temp
        
        self.pos=SkyCoord(ra=self.ra,dec=self.dec, distance=self.distance,  frame='icrs')

    def get_xyz(self):
        """
        set the x,y z attributes of the object

        Args:
            obj (object) : Brown Dwarf object
        """
        gal=self.pos.transform_to('galactic')
        self.x = gal.cartesian.x.to(u.pc).value
        self.y = gal.cartesian.y.to(u.pc).value
        self.z = gal.cartesian.z.to(u.pc).value

class Plot3D:
    """ Plotting in 3d

        Set up a 3D plotting scene

        Attributes:

        plotstars: bool

    """
    def __init__(self, plotstars = False):
        """
        Plotting in 3d

        Args:
            Plot3D object
        """
        self.objects = [] # list of objects to keep track of on the plot
        self.artists = {} # dictionary for keeping track of object names and handles for legend
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        lims = 1
        self.ax.set_xlim(-lims,lims)
        self.ax.set_ylim(-lims,lims)
        self.ax.set_zlim(-lims,lims)
        self._setup_plot() # set up method for putting the sun, labels, and initilize viewing angle

        if plotstars:
            self.plot_stars()

    def _setup_plot(self):
        """
        Setup plot with axis limits and labels. Plot the Sun at (0,0,0)

        Args:
            obj (object) : Brown Dwarf object
        """
        self.ax.set_xlabel("X (pc)")
        self.ax.set_ylabel("Y (pc)")
        self.ax.set_zlabel("Z (pc)")
        self.ax.scatter(0, 0, 0, color='orange', label='Sun', marker = '*')
        self.ax.text(0,0,0, f"Sun", color='orange')
        self.ax.legend()
        self.ax.view_init(elev=0, azim=125)


    def show(self):
        """Displays the interactive plot (in Jupyter)

        Args:
            obj (object): Brown Dwarf object
        """
        display(self.fig)

    def plot_stars(self, catalog = 'Gaia'): 
        """ 
        Plot selection of Milky Way stars
        Args:
            catalog (str) : catalog to query stars from. Default is Gaia
        """
        if catalog == 'Gaia':
            query = """
                        SELECT TOP 1000 source_id, ra, dec, l, b, phot_g_mean_mag
                        FROM gaiadr3.gaia_source
                        WHERE phot_g_mean_mag < 12
                        """
            job = Gaia.launch_job_async(query)
            results = job.get_results()
            l = results['l']
            b = results['b']
            stars = SkyCoord(l=l, b=b, frame='galactic')
            self.ax.scatter(stars.cartesian.x, stars.cartesian.y, stars.cartesian.z, 
                            color = 'black', alpha = 0.005, marker = 'o', label = f'Stars from {catalog}')
            self.ax.legend()

    # function to add object to plot
        
    def add_object(self, obj, show_label=True):
        """ 
        Add new object to plot. Prints object coordinates
        Args:
            obj (object) : Brown Dwarf object
        """
        self.objects.append(obj) 
        obj.get_xyz() # get the x,y and z of object. Note obj must have been initialized as BrownDwarf for this to work

        if hasattr(obj, 'temp'):
            norm = mcolors.Normalize(vmin=200, vmax=2500)
            cmap = cm.Reds
            color = cmap(norm(obj.temp))
            obj.color = color

        if len(self.objects) > 0:
            lims = float(max([x.distance for x in self.objects]).value)
            self.ax.set_xlim(-lims,lims)
            self.ax.set_ylim(-lims,lims)
            self.ax.set_zlim(-lims,lims)
        scatter = self.ax.scatter(obj.x, obj.y, obj.z, color=obj.color, label=obj.name)
        if show_label:
            text = self.ax.text(obj.x, obj.y, obj.z, f" {obj.name}", color=obj.color)

        # add the artist to the dictionary 
        self.artists[obj.name] = [scatter]
        if show_label:
            self.artists[obj.name].append(text)
        self.ax.legend()
        self.fig.canvas.draw()
        print(f"Added: {obj.name} at (x={obj.x:.1f}, y={obj.y:.1f}, z={obj.z:.1f}) pc")


    # function to remove object from plot
    def remove_object(self,name):
        """
        Remove the object from the list 

        Args:
            obj (object) : Brown Dwarf object
            name (str): Name of object
        """
        self.objects = [obj for obj in self.objects if obj.name != name] # keep non removed ones
        # now check for the artist and remove that one
        if name in self.artists:
            for artist in self.artists[name]:
                artist.remove() # remove from dictionary
            del self.artists[name]
            # now fix the legend
            self.fix_legend()
            # redraw
            self.fig.canvas.draw()
            print(f'Removed: {name}!')

    # legend function

    def fix_legend(self):
        """
        Fix the legend from the 3D Plot

        Args:
            obj (object) : Brown Dwarf object
        """
        handles = [] # legend handles
        labels = [] # legend labels

        for obj in self.objects:
            if obj.name in self.artists:
                handles.append(self.artists[obj.name][0])
                labels.append(obj.name)
        # now update the legend
        self.ax.legend(handles, labels)


