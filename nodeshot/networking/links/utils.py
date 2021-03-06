from netdiff import diff


links_legend = [
    {
        "name": "Link",
        "slug": "link",
        "description": "Active links",
        "fill_color": "#00ff00",
        "stroke_color": "#00ff00",
        "stroke_width": 4,
        "text_color": "#ffffff",
    }
]


def get_ifs(topology, link):
    if(topology.type_id==1):
        """ ipv4/6 (any L3 routing protocol) """
        ip_src = Ip.objects.get(address = link[0])
        ip_dst = Ip.objects.get(address = link[1])
        return ip_src.topology, ip_dst.topology
    elif(topology.type_id==2):
        """ mac (batman) """
        if_a = Interface.objects.get(mac = link[0])
        if_b = Interface.objects.get(mac = link[1])
        return if_a, if_b
    else:
        """ error """
        return null, null


def update_topology():
    for topology in Topology.objects.all():
        module = importlib.import_module(topology.backend)
        parser_class_name = topology.backend.split('.')[-1]
        classparsr = getattr(module, parser_class_name)
        njparser = NetJsonParser(to_netjson(topology))
        parser = classparser(topology.url)
        graph_diff = diff(njparser, parser)

        for link in graph_diff['added']:
            if_a, if_b = get_ifs(topology, link)
            Link.objects.create(interface_a=if_a, interface_b=if_b, metric_value=link[2]['weight'])
        for link in graph_diff['removed']:
            if_a, if_b = get_ifs(topology, link)
            try:
                l = Link.objects.get(interface_a=if_a, interface_b=if_b)
                l.delete()
            except Link.DoesNotExist:
                pass


def exist_node(id, nodes):
    return any([node.get('id') == id for node in nodes])


def to_netjson(topology):
    nodes = []
    links = []

    for link in Link.objects.filter(topology=topology):
        if (topology.type_id==1 or topology.type_id==2):
            # TODO
            pass
        elif topology.type_id == 2:
            identifier_a = link.inteface_a.mac
            identifier_b = link.inteface_b.mac

        node_a = {'id': identifier_a}
        node_b = {'id': identifier_b}

        if not exist_node(node_a, nodes):
            nodes.append(node_a)
        if not exist_node(node_b, nodes):
            nodes.append(node_b)
        links.append(link.to_netjson())

    return {
        'type': 'NetworkGraph',
        'protocol': island.get_protocol_display(),
        'version': '0',
        'metric': '0',
        'router_id': island.url,
        'nodes': nodes,
        'links': links
    }
