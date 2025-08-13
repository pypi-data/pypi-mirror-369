from test_data_classes import UMCContent, Sport, League, Person, Collection, Canvas, Campaign
from test_data_keys import CanvasNames, ContentDatas, SportNames, LeagueNames, CompetitorNames, PersonNames, \
    CollectionNames, CanvasTypes, CampaignNames
from test_data_classes import ContentTypes

CONTENT_DATAS = {
    ####################################################################################################
    # SPORTS => LEAGUES/TEAMS/EVENTS
    ####################################################################################################
    ContentDatas.SPORTS: {
        SportNames.CHESS: Sport(
            id='umc.csp.2vvrfwuznd4dakvn3wogioza',
            name='Chess',
            related_content={
            }
        ),
        SportNames.GYM: Sport(
            id='umc.csp.1aye1labjzj5aq29oat5axeag',
            name='Gymnastics',
            related_content={
            }
        ),
        SportNames.SOCCER: Sport(
            id='umc.csp.y1ye10qgphjwmbdsld07rf38',
            name='Soccer',
            related_content={
            }
        ),
        SportNames.BASEBALL: Sport(
            id='umc.csp.3swghpf8lfhfyg9xnn5onmit',
            name='Baseball',
            related_content={
            }
        ),
        SportNames.SOCCER_AS_SHOW: Sport(
            id='umc.cse.5y817v7zm822x2rzm62xg54iu',
            name='Soccer As Show',
            # treat as a show umc tag
            umc_tag='umc.tag.2fg62nvsdml5duil020rgztm5',
            related_content={}
        ),
    },
    ContentDatas.LEAGUES: {
        LeagueNames.MLB: League(
            id='umc.csl.50vezwb1n14iqvdgtxwcpo2z1',
            name='Major League Baseball',
            competitors={
                CompetitorNames.ARIZONA: UMCContent(
                    id='umc.cst.5089wqyx4rtwcqhieokg1bfsy',
                    name='Arizona Diamondbacks',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.CINCINNATI: UMCContent(
                    id='umc.cst.3w8bud3a6ccq0kstucgkqevyv',
                    name='Cincinnati Reds',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.CLEVELAND: UMCContent(
                    id='umc.cst.1838zqsmq6w7ew8qpt73c6cto',
                    name='Cleveland Guardians',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.COLORADO: UMCContent(
                    id='umc.cst.2lwj96e1c12cri7p29oc2id0r',
                    name='Colorado Rockies',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.DETROIT: UMCContent(
                    id='umc.cst.3k7sfmnho8ac6tapydmena7jr',
                    name='Detroit Tigers',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.HOUSTON: UMCContent(
                    id='umc.cst.3jdd8u3sm085xxagevgjgeehp',
                    name='Houston Astros',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.KANSAS_CITY: UMCContent(
                    id='umc.cst.1p4968l0tkaqz5aiipiv57uea',
                    name='Kansas City Royals',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.MILWAUKEE: UMCContent(
                    id='umc.cst.6ulfyndbd9a0q8kqoydvjihdo',
                    name='Milwaukee Brewers',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.MINNESOTA: UMCContent(
                    id='umc.cst.1ezpiz2n3w3y62xpybt4wmjbz',
                    name='Minnesota Twins',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.PITTSBURGH: UMCContent(
                    id='umc.cst.4p8ybharfysdv34xou2vdfdat',
                    name='Pittsburgh Pirates',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.SAN_DIEGO: UMCContent(
                    id='umc.cst.63df5l7qvspk1ulnsbkte43ln',
                    name='San Diego Padres',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.SEATTLE: UMCContent(
                    id='umc.cst.20tumiku41e738yxcn7cre4ga',
                    name='Seattle Mariners',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.ST_LOUIS: UMCContent(
                    id='umc.cst.1rmejsg14wnx8ajhm4bwlsi57',
                    name='St. Louis Cardinals',
                    type=ContentTypes.TEAM
                ),
                CompetitorNames.TEXAS: UMCContent(
                    id='umc.cst.6d346uaal3ldt7z3oerfl71k8',
                    name='Texas Rangers',
                    type=ContentTypes.TEAM
                )
            },
            related_content={
            }
        ),
        LeagueNames.MLS: League(
            id='umc.csl.3c9plmy5skze52ff5ce24mo4g',
            name='Major League Soccer',
            abbreviation='MLS',
            competitors={
                CompetitorNames.SEATTLE: UMCContent(
                    id='umc.cst.3fsre50fs7bbhix862flzbaj4',
                    name='Seattle Sounders FC',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'seattle'
                    }
                ),
                CompetitorNames.SAN_JOSE: UMCContent(
                    id='umc.cst.6gspym9ull3fqbw9tylmhs7jr',
                    name='San Jose Earthquakes',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'sanjose'
                    }
                ),
                CompetitorNames.MIAMI: UMCContent(
                    id='umc.cst.52peuzm5uh6ms5olnckn15i3p',
                    name='Inter Miami CF',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'miami'
                    }
                ),
                CompetitorNames.ATLANTA: UMCContent(
                    id='umc.cst.3ykg5vxse5z5ow87nssp6oojd',
                    name='Atlanta United',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'atlanta'
                    }
                ),
                CompetitorNames.GALAXY: UMCContent(
                    id='umc.cst.k7og69ko6rj30lg2480d376',
                    name='Galaxy Club Page',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'galaxy'
                    }
                ),
                CompetitorNames.LAFC: UMCContent(
                    id='umc.cst.2dawsmn6z7a77otpog04jowi8',
                    name='LAFC club page',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'lafc'
                    }
                ),
                CompetitorNames.DC: UMCContent(
                    id='umc.cst.34dq6dhwewl6nj1t522ln5n0u',
                    name='DC United page',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'dc'
                    }
                ),
                CompetitorNames.MONTREAL: UMCContent(
                    id='umc.cst.2apzse1smd6k4zf714oywbuod',
                    name='CF Montréal',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'montreal'
                    }
                ),
                CompetitorNames.DALLAS: UMCContent(
                    id='umc.cst.5o0zsc41gl10rvafh3anhqicp',
                    name='FC Dallas',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'dallas'
                    }
                ),
                CompetitorNames.NASHVILLE: UMCContent(
                    id='umc.cst.46onf4t748fnaezr18epvj1gb',
                    name='Nashville SC',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'nashville'
                    }
                ),
                CompetitorNames.PORTLAND: UMCContent(
                    id='umc.cst.36ae73uo2tfj8cb58iffcs1gc',
                    name='Portland Timbers',
                    type=ContentTypes.TEAM,
                    related_content={
                        'alias': 'portland'
                    }
                )
            },
            related_content={
            }
        ),
        LeagueNames.MLSNEXT: League(
            id='umc.csl.6pdycu4xw8d8xub4czot6qlz7',
            name='MLS NEXT',
        ),
        LeagueNames.MLSNEXTPRO: League(
            id='umc.csl.3sc5bhnref2h9knzjz6oc1yuy',
            name='MLS NEXT Pro',
        ),
        LeagueNames.LEAGUECUP: League(
            id='umc.csl.2uttzljf6fvxsf5zd5qhd6316',
            name='Leagues Cup',
        ),
        LeagueNames.CAMPEONES: League(
            id='umc.csl.29zmcdp8bu5uw3j3wo9j60ina',
            name='Campeones Cup',
        ),
        LeagueNames.NBA: League(
            id='umc.csl.6weg523v2uut4n0viue8lnchl',
            name='National Basketball Assoc.',
            competitors={
                CompetitorNames.CHICAGO: UMCContent(
                    id='umc.cst.x8sfaovvh1xqlwvrtyzaqtgn',
                    name='Chicago Bulls',
                    type=ContentTypes.TEAM
                )
            },
            related_content={
            }
        ),
        LeagueNames.NHL: League(
            id='umc.csl.1oa93qge192eotcbzpg15bjra',
            name='National Hockey League',
        ),
        LeagueNames.CBK: League(
            id='umc.csl.2cabxc3ovy3ue0g5j8fbeuy47',
            name="Men's College Basketball",
        ),
        LeagueNames.WCBK: League(
            id='umc.csl.2ezxlj5qz3q8mmhqhqsygke17',
            name="Women's College Basketball",
        ),
        LeagueNames.EPL: League(
            id='umc.csl.4uhb3gez2l9v5y5u4nz5zwft6',
            name='epl',
            competitors={
                CompetitorNames.ARSENAL: UMCContent(
                    id='umc.cst.5gx97l2c8jun1ibioji2x3i0y',
                    name='Arsenal FC',
                    type=ContentTypes.TEAM
                )
            },
            related_content={
            }
        ),
        LeagueNames.UCL: League(
            id='umc.csl.54lffyo8yvmkmg37e5id6xxfx',
            name='UEFA Champions League',
        ),
        LeagueNames.BUND: League(
            id='umc.csl.539o5xdl4lsljih7dsmg87vr6',
            name='bund',
        ),
        LeagueNames.LIGA_MX: League(
            id='umc.csl.17bw49ba4e76fklk4prrvw56l',
            name='Liga MX',
        ),
        LeagueNames.LALIGA: League(
            id='umc.csl.3237y6rbrl2qen7f7szomv16p',
            name='liga',
        ),
        LeagueNames.LEAGUE1: League(
            id='umc.csl.1uj0l389fay3c1igfnev1zqog',
            name='France Ligue 1',
        ),
        LeagueNames.SERIEA: League(
            id='umc.csl.1wr618hvywicw1y9ib4uen974',
            name='itsa',
        ),
        LeagueNames.UECL: League(
            id='umc.csl.16ob2p75zv3aspetuakmpaf83',
            name='UEFA Europa League',
        ),
        LeagueNames.NFL: League(
            id='umc.csl.51b2og571wp1v0llpx0u9k86o',
            name='nfl',
        ),
        LeagueNames.WNBA: League(
            id='umc.csl.5dxjk26e7ry0x9p6vuexaqr3f',
            name="Women's National Basketball Assoc.",
        ),
        LeagueNames.NWSL: League(
            id='umc.csl.1ro9cn3yn5gxx2imfvb9vpmna',
            name="National Women's Soccer League",
        ),
        LeagueNames.NCAAF: League(
            id='umc.csl.7h0yrhl69b8vwdwj527eduzr9',
            name='NCAA Football',
        ),
        LeagueNames.NCAAB: League(
            id='umc.csl.2ajer4j70m9rczmty0g3http7',
            name='NCAA Baseball',
        ),
        LeagueNames.NCAAS: League(
            id='umc.csl.68xersvuh1ma3ijo7dphbd9ij',
            name='NCAA Softball',
        ),
        LeagueNames.NCAACWH: League(
            id='umc.csl.531sr7z0mu1e0m0shpznb1kdq',
            name="NCAA Women's Hockey",
        ),
        LeagueNames.NCAACWS: League(
            id='umc.csl.4p9nm91afl96tpj8kpjpb9433',
            name="NCAA College Women's Soccer",
        ),
        LeagueNames.NCAACMS: League(
            id='umc.csl.6cr97ym38axjqqz7a79t8hnq3',
            name="NCAA College Men's Soccer",
        ),
        LeagueNames.CFL: League(
            id='umc.csl.ws0leggk7qs0c464kxdwah2p',
            name='Canadian Football League',
        ),
        LeagueNames.LEAGUESCUP: League(
            id='umc.csl.5z70ltcashjwl8dgwmwxyd3h2',
            name="League's Cup'",
        ),
        LeagueNames.USOC: League(
            id='umc.csl.6skj1cv482vhgq172lfynx177',
            name="USOC",
        ),
        LeagueNames.EUCHM: League(
            id='umc.csl.12nc7ju84nmgbmo3aptcj0bes',
            name="EUCHM",
        ),
        LeagueNames.COPA: League(
            id='umc.csl.1sbpuds5uar8ulxqmo1c2lgg3',
            name="COPA",
        )
    },
    ContentDatas.PERSONS: {
        PersonNames.KIRSTEN_DUNST: Person(
            id='umc.cpc.1j8tm9b297bz01dzkez8x490b',
            name='Kirsten Dunst'
        ),
        PersonNames.JIMMY_KIMMEL: Person(
            id='umc.cpc.355yy0sl4nt6jmialz7pyyoqx',
            name='Jimmy Kimmel'
        ),
        PersonNames.PETER_DINKLAGE: Person(
            id='umc.cpc.2guxyxqxovd1xt2tcpd4pl9as',
            name='Peter Dinklage',
        ),
        PersonNames.TOM_HANKS: Person(
            id='umc.cpc.1aj85ouxcuptpsm73snts9gj2',
            name='Tom Hanks',
        ),
        PersonNames.STEVEN_SEAGAL: Person(
            id='umc.cpc.3vtfndasyrquw5caq8sseg95z',
            name='Steven Seagal',
        ),
        PersonNames.JASON_BLUM: Person(
            id='umc.cpc.2uhrqcvf41rgds67jt5gjjiah',
            name='Jason Blum',
        ),
        PersonNames.BRAD_BIRD: Person(
            id='umc.cpc.7ivvligx81r48542zx97vcopk',
            name='Brad Bird',
        ),
        PersonNames.JAMES_CAMERON: Person(
            id='umc.cpc.4lrx2mxaz5yw3h1sexfbhx4u0',
            name='James Cameron',
        ),
        PersonNames.STEVE_ROGERS: Person(
            id='',
            name='Steve Rogers',
        ),
        PersonNames.RYAN_REYNOLDS: Person(
            id='umc.cpc.piy3otwraylpzhddt5knavle',
            name='Ryan Reynolds'
        ),
        PersonNames.JASON_SUDEIKIS: Person(
            id='umc.cpc.25ep598vpnran7vjban1uob48',
            name='Jason Sudeikis'
        ),
        # Has snapshotUrl vended
        PersonNames.LADY_GAGA: Person(
            id='umc.cpc.5pizy2418ot22my3je7vt3fku',
            name='Lady Gaga'
        ),

        PersonNames.IAN_FRAY: Person(
            id='umc.cpc.1hql8ec51nzp0fg5ss3yat8p2',
            name='Ian Fray'
        ),

        PersonNames.BARTOSZ_SLISZ: Person(
            id='umc.cpc.1yxal7l0r6er2wht8t8ywh0a3',
            name='Bartosz Slisz'
        ),

        PersonNames.LONDON_AGHEDO: Person(
            id='umc.cpc.2f6ztr9uzjfv5u9ayj2cbjfds',
            name='London Aghedo'
        ),

        PersonNames.LIONEL_MESSI: Person(
            id='umc.cpc.mmrpiznqer8pnnktaacgdakn',
            name='Lionel Messi'
        ),

        PersonNames.LUIS_SUAREZ: Person(
            id='umc.cpc.30t14aez3nkfxpte3fvfibjul',
            name='Luis Suarez'
        )

    },
    ContentDatas.AB_TESTING: {
        CollectionNames.NO_TREATMENT_CONTROL: Collection(
            collection_id='edt.col.63c9841d-7696-4d01-b67b-62be57b07f07',
            context_ids=[]
        ),
        CollectionNames.CONTROL_AND_TREATMENT: Collection(
            collection_id='edt.col.63c9839f-ef0e-4c8e-94bf-2ad7dc22dbc5',
            context_ids=[]
        ),
        CollectionNames.AREA1_TREATMENT: Collection(
            collection_id='edt.col.63c97cbc-1739-4af5-af06-62ef307dc241',
            context_ids=[]
        ),
        CollectionNames.AREA2_TREATMENT: Collection(
            collection_id='edt.col.639b551a-1be8-46ca-ab8e-9f314cc95458',
            context_ids=[]
        ),
        CollectionNames.AREA1_CONTROL: Collection(
            collection_id='edt.col.63c98308-2a93-48c2-9652-9cf1f7045a2f',
            context_ids=[]
        ),
        CollectionNames.AREA2_CONTROL: Collection(
            collection_id='edt.col.63ceb06e-5b3e-45b0-8756-7ccb21b904ed',
            context_ids=[]
        ),
        CanvasNames.AB_CAPABILITIES_ONE_AREA_CONTROL_TREATMENT: Canvas(
            canvas_type=CanvasTypes.CANVAS,
            id='edt.cvs.63c984a0-3991-4c6b-83ec-5224ece96b49',
            name='ab_capabilities_one_area_control_treatment'
        ),
        CanvasNames.AB_CAPABILITIES_ONE_AREA: Canvas(
            canvas_type=CanvasTypes.CANVAS,
            id='edt.cvs.63d1a720-eda1-474b-b258-bb5e1a38e137',
            name='ab_capabilities_one_area'
        ),
        CanvasNames.AB_CAPABILITIES_MULTIPLE_AREA: Canvas(
            canvas_type=CanvasTypes.CANVAS,
            id='edt.cvs.63ced940-215d-4503-aedf-472f769c8936',
            name='ab_capabilities_multiple_area'
        )
    }
}
