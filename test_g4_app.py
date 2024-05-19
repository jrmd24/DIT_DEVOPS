from streamlit.testing.v1 import AppTest

at = AppTest.from_file("g4_dc_app.py", default_timeout=320).run()

# at.run()
# class TestG4App(unittest.TestCase):


# at.sidebar
def test_page_1():
    at.sidebar.selectbox(key="action").select("Télécharger données collectées").run()
    # at.button[0].click().run()
    assert not at.exception, at.exception[0].message
    button_labels = ["Voitures", "Motos et scooters", "Equipements"]
    dataframe_sizes = [(650, 9), (281, 9), (994, 9)]
    for i, label in enumerate(button_labels):
        print(label)
        at.button[i].click().run()
        assert at.button[i].label == label
        # assert at.download_button[0].label == "Download data as CSV"
        assert at.dataframe[0] is not None
        # assert len(at.dataframe) == 3
        # print(len(at.dataframe[0].data))
        # assert len(at.dataframe[0].data) == dataframe_sizes[i]
        assert at.dataframe[0].value.shape == dataframe_sizes[i]
    # assert (at.dataframe[0].height, at.dataframe[0].width) == (650, 9)
    # assert pd.DataFrame(at.dataframe[0].data).shape == (650, 9)


def test_page_2():

    at.sidebar.selectbox(key="action").select("Collecter données").run()
    assert not at.exception, at.exception[0].message

    at.sidebar.selectbox(key="num_pages").select("3").run()
    # at.button[1].click().run()
    assert not at.exception, at.exception[0].message

    table_captions = ["Voitures", "Motos", "Equipements"]

    print(at.title)
    assert len(at.title) >= 3

    for i, caption in enumerate(at.title[:3]):
        assert caption.value == table_captions[i]

    assert len(at.dataframe) == 3
    for i, dt in enumerate(at.dataframe):
        assert dt is not None
        assert len(dt.data) > 400


# test_page_1()
# test_page_2()
