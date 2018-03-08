from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from itertools import chain
from api.models import GEM, Author
from api.serializers import *

import urllib.request
import requests
import re
import logging

def is_model_valid(function):
    # TODO not working yet
    def wrap(request, *args, **kwargs):
        entry = Entry.objects.get(pk=kwargs['model'])
        return True

    return wrap

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view()
def model_list(request):
    """
    List all Genome-scale metabolic models (GEMs) that are in the database
    """
    models = GEM.objects.all()
    serializer = GEMSerializer(models, many=True)
    return JSONResponse(serializer.data)


@api_view()
def get_model(request, id):
    """
    Return all known information for a given model, supply its id, for example 1
    """
    try:
        model = GEM.objects.get(id=id)
    except GEM.DoesNotExist:
        return HttpResponse(status=404)

    serializer = GEMSerializer(model)
    return JSONResponse(serializer.data)


@api_view()
def author_list(request):
    """
    List all authors for all the GEMs in the database
    """
    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)
    return JSONResponse(serializer.data)


@api_view()
def get_author(request, id):
    """
    Return all the information we have about a specific author,
    supply an id (for example 1)
    """
    try:
        author = Author.objects.get(id=id)
    except Author.DoesNotExist:
        return HttpResponse(status=404)

    serializer = AuthorSerializer(author)
    return JSONResponse(serializer.data)


@api_view()
def reaction_list(request, model):
    """
    Returns ALL reactions
    (well actually only the first 20)
    """
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    reactions = Reaction.objects.using(model).all()[offset:(offset+limit)]
    serializer = ReactionSerializer(reactions, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def get_reaction(request, model, id):
    """
    Return all the information we have about a reaction,
    supply an id (for example R_HMR_3905).
    Please note that this also pulls out the associated annotations
    that we have for the individual metabolites that is part of
    the reaction, and the proteins that are modifying the reaction
    """
    try:
        reaction = Reaction.objects.using(model).get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    reactionserializer = ReactionSerializer(reaction, context={'model': model})
    pmids = ReactionReference.objects.using(model).filter(reaction_id=id)
    if pmids.count():
        pmidserializer = ReactionReferenceSerializer(pmids, many=True)
        url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
               '?db=pubmed&retmode=json&id={}'.format(
                   ','.join([x['pmid'].replace('PMID:', '')
                             for x in pmidserializer.data])))
        pmidsresponse = requests.get(url).json()['result']
    else:
        pmidsresponse = {}

    return JSONResponse({'reaction': reactionserializer.data,
                         'pmids': pmidsresponse})


@api_view()
def reaction_reactant_list(request, model, id):
    """
    For a given reaction show ALL the metabolites that are consumed,
    supply a reaction id (for example R_HMR_6414).
    Please note also pulls out the annotations we have for these
    metabolites.
    """
    try:
        reaction = Reaction.objects.using(model).get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reaction.reactants, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def get_reaction_reactant(request, model, reaction_id, reactant_id):
    """
    For a given reaction, show the annotations for a specific reactant,
    supply a reaction id (for example R_HMR_3907) AND
    a metabolite id (for example M_m01796c).
    """
    try:
        reaction = Reaction.objects.using(model).get(id=reaction_id)
        reactant = reaction.reactants.get(id=reactant_id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reactant, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def reaction_product_list(request, model, id):
    """
    For a given reaction show the metabolites that are produced,
    supply a reaction id (for example R_HMR_6414).
    Please note also pulls out the annotations we have for these
    metabolites.
    """
    try:
        reaction = Reaction.objects.using(model).get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reaction.products, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def get_reaction_product(request, model, reaction_id, product_id):
    """
    For a given reaction, show the annotations for a specific product,
    supply a reaction id (for example R_HMR_3907) AND
    a metabolite id (for example M_m01796c).
    """
    try:
        reaction = Reaction.objects.using(model).get(id=reaction_id)
        product = reaction.products.get(id=product_id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(product, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def reaction_modifier_list(request, model, id):
    """
    For a given reaction show the proteins that are modifying it,
    supply a reaction id (for example R_HMR_6414).
    Please note also pulls out the annotations we have for these
    enzymes.
    """
    try:
        reaction = Reaction.objects.using(model).get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reaction.modifiers, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def get_reaction_modifier(request, model, reaction_id, modifier_id):
    """
    For a given reaction, show the annotations for a specific product,
    supply a reaction id (for example R_HMR_3907) AND
    a enzyme id (for example E_1209).
    """
    try:
        reaction = Reaction.objects.using(model).get(id=reaction_id)
        modifier = reaction.modifiers.get(id=modifier_id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(modifier, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def component_list(request, model):
    """
    Return the first 20 reaction components in the database,
    eg this could technically be either a reactant (metabolite),
    a product (metabolite), or the modifying enzyme.
    """
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))

    name = request.query_params.get('name', None)
    if name:
        components = ReactionComponent.objects.using(model).filter(
                Q(id__icontains=name) |
                Q(long_name__icontains=name) |
                Q(short_name__icontains=name)
            )[offset:(offset+limit)]
    else:
        components = ReactionComponent.objects.using(model).all()[offset:(offset+limit)]

    serializer = ReactionComponentSerializer(components, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def get_component(request, model, id):
    """
    Return all information for a given reaction component,
    eg this could technically be either
    a reactant (metabolite, for example M_m01796c),
    a product (metabolite, for example M_m01249c),
    or the modifying enzyme (for example E_3328).
    """
    try:
        component = ReactionComponent.objects.using(model).get(Q(id=id) |
                                                               Q(long_name=id))
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(component, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def currency_metabolite_list(request, model, id):
    """
    For a given reaction component, list all reactions in which its a currency metabolite,
    supply an id (for example M_m00003c)
    """
    try:
        component = ReactionComponent.objects.using(model).get(id=id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    serializer = CurrencyMetaboliteSerializer(component.currency_metabolites, many=True)
    return JSONResponse(serializer.data)

#@api_view()
#def component_expression_list(request, id):
#    tissue = request.query_params.get('tissue', '')
#    expression_type = request.query_params.get('expression_type', '')
#    expressions = ExpressionData.objects.filter(
#            Q(reaction_component=id) &
#            Q(tissue__icontains=tissue) &
#            Q(expression_type__icontains=expression_type)
#        )

#    serializer = ExpressionDataSerializer(expressions, many=True)
#    return JSONResponse(serializer.data)


@api_view()
def interaction_partner_list(request, model, id):
    """
    For a given reaction component, pull out all first order interaction partners,
    supply a reaction component id (eg either metabolite or enzyme id,
    for example E_1008).
    """
    try:
        component = ReactionComponent.objects.using(model).get(id=id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions = list(chain(component.reactions_as_reactant.all(), component.reactions_as_product.all(), component.reactions_as_modifier.all()))
    serializer = InteractionPartnerSerializer(reactions, many=True)
    return JSONResponse(serializer.data)


@api_view()
def get_component_with_interaction_partners(request, model, id):
    """
    Get the annotation + interaction partners for a given reaction component,
    supply an id (for example M_m01954g or E_3640)
    """
    try:
        component = ReactionComponent.objects.using(model).get(Q(id=id) | Q(long_name=id))
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    component_serializer = ReactionComponentSerializer(component, context={'model': model})

    reactions_count = component.reactions_as_reactant.count() + \
            component.reactions_as_product.count() + \
            component.reactions_as_modifier.count()

    if reactions_count > 100:
        return HttpResponse(status=406)

    reactions = list(chain(
        component.reactions_as_reactant.all(),
        component.reactions_as_product.all(),
        component.reactions_as_modifier.all()
    ))
    reactions_serializer = InteractionPartnerSerializer(reactions, many=True)

    result = {
             'component': component_serializer.data,
             'reactions': reactions_serializer.data
             }

    return JSONResponse(result)


@api_view()
def enzyme_list(request, model):
    """
    List the first 20 enzymes in the database
    """
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))

    enzymes = ReactionComponent.objects.using(model).filter(component_type='enzyme')[offset:(offset+limit)]

    serializer = ReactionComponentSerializer(enzymes, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def connected_metabolites(request, model, id):
    """
    For a given enzyme pull out the metabolites that are in any of the modified reactions,
    supply an enzyme id (for example E_3328) or an ensembl gene identifier
    (for example ENSG00000180011).
    If more than 10 reactions, then it will return only the actual reactions,
    otherwise it will pull out the metabolites and their annotations as well.
    """
    try:
        enzyme = ReactionComponent.objects.using(model).get(
                Q(component_type='enzyme') &
                (Q(id=id) | Q(long_name=id))
            )
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions_count = enzyme.reactions_as_modifier.count()

    reactions = Reaction.objects.using(model).filter(
            Q(reactionmodifier__modifier_id=enzyme.id)
            ).distinct()
    serializer = ReactionLiteSerializer(reactions, many=True, context={'model': model})

    result =  {
        'enzyme' : ReactionComponentSerializer(enzyme, context={'model': model}).data,
        'reactions': serializer.data
    }

    return JSONResponse(result)


@api_view()
def get_metabolite_reactions(request, model, reaction_component_id):
    """
    In which reactions does a given metabolite occur,
    supply a metabolite id (for example M_m00003c).
    Here there are two possibilities,
    only return the list of reactions for the given compartment (!),
    or alternatively in all compartments.
    """
    expandAllCompartment = False
    try:
        component = ReactionComponent.objects.using(model).get(Q(id=reaction_component_id) |
                                                               Q(long_name=reaction_component_id))
    except ReactionComponent.DoesNotExist:
        try:
            component = ReactionComponent.objects.using(model).filter(
                                                      (Q(id__icontains=reaction_component_id) |
                                                       Q(long_name=reaction_component_id)) &
                                                       Q(component_type='metabolite')
                                                   )
            expandAllCompartment = True
            logging.warn(component);
        except ReactionComponent.DoesNotExist:
            return HttpResponse(status=404)

    if expandAllCompartment:
        reactions = Reaction.objects.using(model).filter(Q(reactionproduct__product_id__in=component) |
                                                         Q(reactionreactant__reactant_id__in=component))[:200]
    else:
        if component.component_type != 'metabolite':
            return HttpResponseBadRequest('The provided reaction component is not a metabolite.')

        reactions = Reaction.objects.using(model).filter(Q(reactionproduct__product_id=reaction_component_id) |
                                                         Q(reactionreactant__reactant_id=reaction_component_id))[:200]

    serializer = ReactionLiteSerializer(reactions, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
def get_metabolite_reactome(request, reaction_component_id, reaction_id):
    """
    For a given reaction component, pull out all reactions in which it occurs,
    and then for these pull out all metabolites, supply an id, for example M_m00674c.
    """
    try:
        component = ReactionComponent.objects.get(id=reaction_component_id)
        reaction = Reaction.objects.get(id=reaction_id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type != 'metabolite':
        return HttpResponseBadRequest('The provided reaction component is not a metabolite.')

    modifiers = ReactionComponent.objects.filter(reactionmodifier__reaction_id=reaction.id)
    __reactants = ReactionComponent.objects.filter(reactionreactant__reaction_id=reaction.id)
    __products = ReactionComponent.objects.filter(reactionproduct__reaction_id=reaction.id)

    reactants = map(lambda
            rc: CurrencyMetaboliteReactionComponent(
                reaction_component=rc,
                reaction_id = reaction.id),
            __reactants)
    products = map(lambda
            rc: CurrencyMetaboliteReactionComponent(
                reaction_component=rc,
                reaction_id = reaction.id),
            __products)

    reaction_serializer = ReactionSerializer(reaction)
    modifiers_serializer = ReactionComponentSerializer(modifiers, many=True)
    reactants_serializer = CurrencyMetaboliteReactionComponentSerializer(reactants, many=True)
    products_serializer = CurrencyMetaboliteReactionComponentSerializer(products, many=True)

    result = reaction_serializer.data
    result['modifiers'] = modifiers_serializer.data
    result['reactants'] = reactants_serializer.data
    result['products'] = products_serializer.data

    return JSONResponse(result)


def rewriteEquation(term):
    # TODO there is probably something better to do here
    term = term.replace("+", " + ")
    term = term.replace("=>", " => ")
    term = re.sub("\\s{2,}", " ", term)
    term = term.strip()
    term = re.sub("(NA|NADP|H)\s\+\s\[", "\g<1>+[", term, flags=re.IGNORECASE)
    term = re.sub("(NA|NADP|H)\s\+(\s=>|$)", "\g<1>+\g<2>", term, flags=re.IGNORECASE)
    rp = term.split('=>')
    if len(rp) > 1:
        reactants = rp[0].split(' + ')
        for i in range(len(reactants)):
            reactants[i] = reactants[i].strip()
            if reactants[i] and not re.match(".+\[.\]$", reactants[i]):
                reactants[i] = reactants[i] + "[_]"
        products = rp[1].split(' + ')
        for i in range(len(products)):
            products[i] = products[i].strip()
            if products[i] and not re.match(".+\[.\]$", products[i]):
                products[i] = products[i] + "[_]"
        reactants = " + ".join(reactants)
        products = " + ".join(products)
        return "%%%s => %s%%" % (reactants, products)
    else:
        elements = rp[0].split(' + ')
        for i in range(len(elements)):
            elements[i] = elements[i].strip()
            if elements[i] and not re.match(".+\[.\]$", elements[i]):
                elements[i] = elements[i] + "[_]"

        elements = " + ".join(elements)
        return "%%%s%%" % elements


@api_view()
def search(request, model, term):
    """
    Searches for the term in metabolites, enzymes, subsystems, reactions, and reaction_components.
    Metabolites: kegg_id, hmdb_id, hmdb_name contains
    Enzymes (uniprot_acc)
    Subsystems (name contains)
    Reactions (equation contains)
    ReactionComponent (id, short name contains, long name contains, formula contains)
    """
    if len(term.strip()) < 2:
        return HttpResponse(status=404)

    if model == 'all':
        models = ['hmr2']
        limit = 1000
    else:
        models = [model]
        limit = 50

    for model in models:
        if model == 'ymr':
            # TODO remove
            continue

        metabolites = Metabolite.objects.using(model).filter(
            Q(kegg__iexact=term) |
            Q(hmdb__iexact=term) |
            Q(hmdb_name__icontains=term)
        )

        enzymes = Enzyme.objects.using(model).filter(
            Q(uniprot_acc__iexact=term)
        )

        compartments = Compartment.objects.using(model).filter(name__icontains=term)

        subsystems = Subsystem.objects.using(model).filter(
            Q(name__icontains=term) |
            Q(external_id__iexact=term)
        )

        reactions = []
        term = term.replace("→", "=>")
        term = term.replace("⇨", "=>")
        term = term.replace("->", "=>")
        if term.strip() not in ['+', '=>']:
            termEq = re.sub("[\(\[\{]\s?(.)\s?[\)\]\}]", "[\g<1>]", term)

            reactions = Reaction.objects.using(model).filter(
                Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(equation__icontains=termEq) |
                Q(ec__iexact=term) |
                Q(sbo_id__iexact=term)
            )[:limit]

            termEq = None
            reactions2 = []
            if '+' in term or '=>' in term:
                termEq = rewriteEquation(term)
                reactions2 = Reaction.objects.using(model).extra(
                    where=["equation::text ILIKE %s"], params=[termEq]
                )[:limit]
            reactions = list(chain(reactions, reactions2))

        components = ReactionComponent.objects.using(model).filter(
                Q(id__iexact=term) |
                Q(short_name__icontains=term) |
                Q(long_name__icontains=term) |
                Q(formula__icontains=term) |
                Q(metabolite__in=metabolites) |
                Q(enzyme__in=enzymes)
            ).order_by('short_name')[:limit]

        if (components.count() + compartments.count() + subsystems.count() + len(reactions))== 0:
            return HttpResponse(status=404)

        RCserializer = ReactionComponentSearchSerializer(components, many=True)
        compartmentSerializer = CompartmentSerializer(compartments, many=True)
        subsystemSerializer = SubsystemSerializer(subsystems, many=True, context={'model': model})
        reactionSerializer = ReactionSearchSerializer(reactions, many=True, context={'model': model})

    results = {
        'reactionComponent': RCserializer.data,
        'compartment': compartmentSerializer.data,
        'subsystem': subsystemSerializer.data,
        'reaction': reactionSerializer.data
    }


    return JSONResponse(results)


@api_view(['POST'])
def convert_to_reaction_component_ids(request, model, compartment_name=None):
    arrayTerms = [el.strip() for el in request.data['data'] if len(el) != 0]
    if not arrayTerms:
        return JSONResponse({})

    query = Q()
    reaction_query = Q()
    for term in arrayTerms:
        query |= Q(id__iexact=term)
        reaction_query |= Q(id__iexact=term)
        query |= Q(short_name__iexact=term)
        query |= Q(long_name__iexact=term)

    # get the list of component id
    reaction_component_ids = ReactionComponent.objects.using(model).filter(query).values_list('id');

    # get the list of reaction id
    reaction_ids = Reaction.objects.using(model).filter(reaction_query).values_list('id')

    if not reaction_component_ids and not reaction_ids:
        return HttpResponse(status=404)

    if not compartment_name:
        # get the compartment id for each component id
        rcci = ReactionComponentCompartmentSvg.objects.using(model) \
        .filter(Q(component_id__in=reaction_component_ids)) \
        .select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'component_id')

        # get the compartment id for each reaction id
        rci = ReactionCompartmentSvg.objects.using(model).filter(Q(reaction_id__in=reaction_ids)) \
        .select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'reaction_id')

    else:
        try:
            compartment = CompartmentSvg.objects.using(model).get(name__iexact=compartment_name)
            compartmentID = compartment.compartment
        except CompartmentSvg.DoesNotExist:
            return HttpResponse(status=404)

        # get the component ids in the input compartment
        rcci = ReactionComponentCompartmentSvg.objects.using(model).filter(
                Q(component_id__in=reaction_component_ids) & Q(Compartmentsvg_id=compartmentID)
            ).select_related('Compartmentsvg') \
            .values_list('compartmentsvg__display_name', 'component_id')

        # get the reaction ids in the input compartment
        rci = ReactionCompartmentSvg.objects.using(model).filter(
            Q(reaction_id__in=reaction_ids) & Q(Compartmentsvg_id=compartmentID)
        ).select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'reaction_id')

        if not rcci.count() and not rci.count():
            return HttpResponse(status=404)

    results = reactionComponents = list(chain(rcci, rci))
    return JSONResponse(results)


@api_view()
def get_subsystem(request, model, subsystem_name):
    """
    For a given subsystem name, get all containing metabolites, enzymes, and reactions.
    """
    try:
        subsystem = Subsystem.objects.using(model).get(name__iexact=subsystem_name)
        subsystem_id = subsystem.id
    except Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        s = Subsystem.objects.using(model).get(id=subsystem_id)
    except Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    smsQuerySet = SubsystemMetabolite.objects.using(model).filter(subsystem_id=subsystem_id).select_related("reaction_component")
    sesQuerySet = SubsystemEnzyme.objects.using(model).filter(subsystem_id=subsystem_id).select_related("reaction_component") # FIXME contains metabolite ids not enzyme
    srsQuerySet = SubsystemReaction.objects.using(model).filter(subsystem_id=subsystem_id).select_related("reaction")

    sms = []; ses = []; srs = [];
    for m in smsQuerySet:
        sms.append(m.reaction_component)
    for e in sesQuerySet:
        ses.append(e.reaction_component)
    for r in srsQuerySet:
        srs.append(r.reaction)

    results = {
        'subsystemAnnotations': SubsystemSerializer(s, context={'model': model}).data,
        'metabolites': ReactionComponentLiteSerializer(sms, many=True, context={'model': model}).data,
        'enzymes': ReactionComponentLiteSerializer(ses, many=True, context={'model': model}).data,
        'reactions': ReactionLiteSerializer(srs, many=True, context={'model': model}).data
    }

    return JSONResponse(results)


@api_view()
def get_subsystems(request, model):
    """
    List all subsystems/pathways/collection of reactions for the given model
    """
    try:
        subsystems = Subsystem.objects.using(model).all()
    except Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    serializer = SubsystemSerializer(subsystems, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
def get_subsystem_coordinates(request, model, subsystem_name, compartment_name=False):
    """
    For a given subsystem name, get the compartment name and X,Y locations in the corresponding SVG map.
    """

    logging.warn(subsystem_name)

    try:
        subsystem = Subsystem.objects.using(model).get(name__iexact=subsystem_name)
        subsystem_id = subsystem.id
    except Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        if not compartment_name:
            tileSubsystem = TileSubsystem.objects.using(model).get(subsystem=subsystem_id, is_main=True)
        else:
            try:
                compartment = CompartmentSvg.objects.using(model).get(name__iexact=compartment_name)
            except CompartmentSvg.DoesNotExist:
                return HttpResponse(status=404)
            tileSubsystem = TileSubsystem.objects.using(model).get(subsystem_id=subsystem_id, compartment=compartment)

    except TileSubsystem.DoesNotExist:
        return HttpResponse(status=404)
    serializer = TileSubsystemSerializer(tileSubsystem)

    return JSONResponse(serializer.data)


@api_view()
def get_compartment(request, model, compartment_name):
    try:
        compartment = CompartmentSvg.objects.using(model).get(name__iexact=compartment_name)
    except CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    serializer = CompartmentSvgSerializer(compartment)

    return JSONResponse(serializer.data)


@api_view()
def get_compartment_information(request, model):
    try:
        compartment_svg_info = CompartmentSvg.objects.using(model).all()
        compartment_info = Compartment.objects.using(model).all()
    except CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    compartmentSvgSerializer = CompartmentSvgSerializer(compartment_svg_info, many=True)

    # get stats from Compartment and replace it
    compartmentSerializer = CompartmentSerializer(compartment_info, many=True)
    d = {}
    for el in compartmentSerializer.data:
        d[el['name']] = el

    for el in compartmentSvgSerializer.data:
        values = d[el['compartment']]
        el['nr_reactions'] = values['nr_reactions']
        el['nr_metabolites'] = values['nr_metabolites']
        el['nr_enzymes'] = values['nr_enzymes']
        el['nr_subsystems'] = values['nr_subsystems']

    return JSONResponse(compartmentSvgSerializer.data)


#=========================================================================================================
# For the Models database


@api_view()
def get_gemodel(request, id):
    """
    For a given model id or label, pull out everything we know about the GEM.
    """
    try: 
        int(id)
        is_int = True
    except ValueError:
        is_int = False

    try:
        if is_int:
            model = GEModel.objects.get(id=id)
        else:
            if id == "HMR2":
                id = "v2.00"
            model = GEModel.objects.get(label=id)
    except GEModel.DoesNotExist:
        return HttpResponse(status=404)

    serializer = GEModelSerializer(model)

    return JSONResponse(serializer.data)


@api_view()
def get_gemodels(request):
    """
    List all GEMs that the group have made
    """
    import urllib
    import json
    import base64
    # get models from database
    serializer = GEModelListSerializer(GEModel.objects.all(), many=True)
    # serializer = None
    # get models from git
    '''list_repo = []
    try:
        URL = 'https://api.github.com/orgs/SysBioChalmers/repos'
        result = urllib.request.urlopen(URL)
        list_repo = json.loads(result.read().decode('UTF-8'))
    except Exception as e:
        logging.warn(e)
        pass
        # return HttpResponse(status=400)

    for repo in list_repo:
        logging.warn(repo['name'])
        if repo['name'].startswith('GEM_') or False:
            try:
                result = urllib.request.urlopen(repo['url'] + '/contents/README.md?ref=master')
                readme = json.loads(result.read().decode('UTF-8'))['content']
            except Exception as e:
                logging.warn(e)
                continue

            readme_content = base64.b64decode(readme)
            logging.warn(readme)
            d = parse_readme_file(readme_content)
            # TODO make GEM objects and json to current serializer

            break'''

    return JSONResponse(serializer.data)


def parse_readme_file(content):
    d = {}
    key_entry = {
        'name': 'label',
    }
    parse_entries = False
    for line in content.decode('UTF-8'):
        if line.startswith("| Name |"):
            if not parse_entries:
                parse_entries = True
            else:
                break

        if parse_entries:
            entry, value = line.split('\t')
            d[key_entry[entry]] = value.strip()

    return d


@api_view()
def get_db_json(request, model, component_name=None, ctype=None, dup_meta=False):
    if component_name:
        if ctype == 'compartment':
            try:
                compartment = Compartment.objects.using(model).get(name__iexact=component_name)
            except Subsystem.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = ReactionCompartment.objects.using(model). \
                filter(compartment=compartment).values_list('reaction', flat=True)
            reactions = Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'modifiers')
        else:
            try:
                subsystem = Subsystem.objects.using(model).get(name__iexact=component_name)
            except Subsystem.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = SubsystemReaction.objects.using(model). \
                filter(subsystem=subsystem).values_list('reaction', flat=True)
            reactions = Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'modifiers')
    else:
        reactions = Reaction.objects.using(model).all().prefetch_related('reactants', 'products', 'modifiers')

    nodes = {}
    links = {}

    duplicateEnzyme = True
    duplicatedEnz= {}
    duplicateMetabolite = dup_meta
    duplicatedId = {}

    duplicateMetaName = {'ATP', 'ADP', 'Pi', 'PPi', 'H2O', 'O2', 'PI pool', 'H+', \
     'NADP', 'NADP+', 'NADH', 'NAD+', 'CoA', 'NADPH', 'acetyl-CoA', 'FAD', 'FADH'}

    for r in reactions:
        reaction = {
            'group': 'reaction',
            'id': r.id,
            'name': r.id,
        }
        nodes[r.id] = reaction;

        for m in r.reactants.all():
            duplicateCurrentMeta = False
            if m.short_name in duplicateMetaName:
                duplicateCurrentMeta = True

            doMeta = True;
            metabolite = None;
            mid = m.id
            if duplicateMetabolite:
                if mid not in nodes:
                    duplicatedId[mid] = 0
                elif duplicateCurrentMeta:
                    duplicatedId[m.id] += 1
                    mid = "%s-%s" % (m.id, duplicatedId[m.id])
                else:
                    doMeta = False;

            if doMeta:
                metabolite = {
                    'group': 'metabolite',
                    'id': mid,
                    'rid': m.id,
                    'name': m.short_name or m.long_name,
                }

                nodes[mid] = metabolite;

            rel = {
              'id': mid + "-" + r.id,
              'source': mid,
              'target': r.id,
              'group': 'fe',
              'rev': r.is_reversible,
            }
            links[rel['id']] = rel;

        for m in r.products.all():
            duplicateCurrentMeta = False
            if m.short_name in duplicateMetaName:
                duplicateCurrentMeta = True

            doMeta = True;
            metabolite = None
            mid = m.id;
            if duplicateMetabolite:
                if mid not in nodes:
                    duplicatedId[mid] = 0
                elif duplicateCurrentMeta:
                    duplicatedId[m.id] += 1
                    mid = "%s-%s" % (m.id, duplicatedId[m.id])
                else:
                    doMeta = False

            if doMeta:
                metabolite = {
                    'group': 'metabolite',
                    'id': mid,
                    'rid': m.id,
                    'name': m.short_name or m.long_name,
                }

                nodes[mid] = metabolite

            rel = {
              'id': r.id + "-" + mid,
              'source': r.id,
              'target': mid,
              'group': 'fe',
              'rev': r.is_reversible,
            }
            links[rel['id']] = rel

        for e in r.modifiers.all():
            eid = e.id;
            if eid in nodes:
                duplicatedEnz[eid] += 1;
                eid = "%s-%s" % (eid, duplicatedEnz[eid])
            else:
                duplicatedEnz[eid] = 0;

            enzyme = {
              'id': eid,
              'group': 'enzyme',
              'name': e.short_name or e.long_name,
            }
            nodes[eid] = enzyme;

            rel = {
              'id': eid + "-" + r.id,
              'source': eid,
              'target': r.id,
              'group': 'ee',
              'rev': r.is_reversible,
            }
            links[rel['id']] = rel

    results = {
        'nodes': [v for k, v in nodes.items()],
        'links': [v for k, v in links.items()],
    }

    return JSONResponse(results)


#####################################################################################

@api_view(['POST'])
def get_HPA_xml_content(request):
    url = request.data['url']
    with urllib.request.urlopen(url) as response:
        data = response.read()

    import gzip
    ddata = gzip.decompress(data)

    return HttpResponse(ddata)

@api_view()
def HPA_enzyme_info(request, ensembl_id):
    try:
        res = ReactionComponent.objects.using('hmr2').get(long_name=ensembl_id)
        rcid = res.id
    except:
        return JSONResponse([])

    subs = Subsystem.objects.using('hmr2').filter(
            Q(id__in=SubsystemEnzyme.objects.using('hmr2').filter(reaction_component_id=rcid).values('subsystem_id')) &
            ~Q(system='Collection of reactions')
        ).values('id', 'name', 'nr_reactions', 'nr_enzymes', 'nr_metabolites', 'nr_unique_metabolites')

    result = []
    for sub in subs.all():
        # get the reactions
        reactions = SubsystemReaction.objects.using('hmr2').filter(subsystem_id=sub['id']).values('reaction_id')
        compartments = Compartment.objects.using('hmr2').filter(
            id__in=SubsystemCompartment.objects.using('hmr2').filter(subsystem_id=sub['id']).values('compartment_id').distinct()
        ).values_list('name', flat=True)
        sub['compartments'] = list(compartments)
        sub['reactions_catalysed'] = ReactionModifier.objects.using('hmr2').filter(Q(reaction__in=reactions) & Q(modifier_id=rcid)).count()
        del sub['id']
        result.append(sub)

    return JSONResponse(result)