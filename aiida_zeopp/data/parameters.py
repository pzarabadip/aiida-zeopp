from voluptuous import Schema, Any, ExactSequence
from aiida.orm.data.parameter import ParameterData

input_dict = {
    'cssr': (bool, 'structure_cssr'),
    'v1': (bool, 'structure_v1'),
    'xyz': (bool, 'structure_xyz'),
    'nt2': (bool, 'network_nt2'),
    'res': (bool, 'free_sphere_res'),
    'zvis': (bool, 'network_zvis'),
    'axs': (float, 'nodes_axs'),
    'sa': (ExactSequence([float, float, int]), 'surface_area_sa'),
    'vol': (ExactSequence([float, float, int]), 'volume_vol'),
    'volpo': (ExactSequence([float, float, int]), 'pore_volume_volpo'),
    'block': (ExactSequence([float, int]), 'block'),
    'psd': (ExactSequence([float, float, int]), 'psd'),
    'chan': (float, 'channels_chan'),
    # radfile is optional
    'r': (Any(basestring, bool), 'radii_rad'),
}


class NetworkParameters(ParameterData):
    """ Command line parameters for zeo++ network binary
    """

    schema = Schema({k: input_dict[k][0] for k in input_dict})

    _OUTPUT_FILE_PREFIX = "out.{}"

    # pylint: disable=redefined-builtin, too-many-function-args
    def __init__(self, dict=None, **kwargs):
        """
        Constructor for the data class

        Usage: ``NetworkParameters(dict={'cssr': True})``

        .. note:: As of 2017-09, the constructor must also support a single dbnode
          argument (to reconstruct the object from a database node).
          For this reason, positional arguments are not allowed.
        """
        if 'dbnode' in kwargs:
            super(NetworkParameters, self).__init__(**kwargs)
        else:
            # set dictionary of ParameterData
            super(NetworkParameters, self).__init__(dict=dict, **kwargs)
            dict = self.validate(dict)

    def validate(self, parameters_dict):
        """validate parameters"""
        return NetworkParameters.schema(parameters_dict)

    def cmdline_params(self, input_file_name=None):
        """Synthesize command line parameters
        
        e.g. [['-r'], ['-axs', '0.4', 'out.axs']]
        """
        pm_dict = self.get_dict()

        parameters = []
        for k, v in pm_dict.iteritems():

            parameter = ['-{}'.format(k)]
            if isinstance(v, bool):
                pass
            elif isinstance(v, list):
                parameter += v
            else:
                parameter += [v]

            # add output file name (except for -r)
            if k != 'r':
                parameter += [self._OUTPUT_FILE_PREFIX.format(k)]

            parameters += parameter

        if input_file_name is not None:
            parameters += [input_file_name]

        return map(str, parameters)

    @property
    def output_files(self):
        """Return list of output files to be retrieved"""
        pm_dict = self.get_dict()

        output_list = []
        for k in pm_dict.keys():
            if k != 'r':
                output_list += [self._OUTPUT_FILE_PREFIX.format(k)]

        return output_list

    @property
    def output_parsers(self):
        """Return list of output parsers to use.

        parameters
        ----------
        parameters: aiida_zeopp.data.parameters.NetworkParameters object
            the parameters object used to generate the cmdline parameters

        returns
        -------
        parsers: list
            List of parsers to be used for each output file.
            List element is None, if parser is not implemented.
        """
        import aiida_zeopp.parsers.plain as pp
        #import aiida_zeopp.parsers.structure as sp

        pm_dict = self.get_dict()
        parsers = []

        for k in pm_dict.keys():
            if k == 'vol':
                parsers += [pp.AVolumeParser]
            elif k == 'volpo':
                parsers += [pp.PoreVolumeParser]
            elif k == 'sa':
                parsers += [pp.SurfaceAreaParser]
            elif k == 'res':
                parsers += [pp.ResParser]
            #elif k == 'cssr':
            #    parsers += [sp.CssrParser]
            else:
                parsers += [None]

        return parsers

    @property
    def output_links(self):
        """Return list of output link names"""
        pm_dict = self.get_dict()

        output_links = []
        for k in pm_dict.keys():
            if k != 'r':
                output_links += [input_dict[k][1]]

        return output_links
