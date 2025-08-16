import numpy as np



def model_tester(
    model_maker,
    model_args,
    model_kwargs,
    data,
    test_mode=True,
    expected_data=None,
    tolerance=None,
    force_tolerance=None,
):
    seed = 42
    np.random.seed(seed)

    # Data split:
    training_data = data[0 : len(data) // 2]
    training_energies = np.array([atoms.get_potential_energy() for atoms in training_data])
    test_data = data[len(data) // 2 :]

    # Make model instance:
    model = model_maker(*model_args, **model_kwargs)

    # Train the model:
    model.train(training_data)

    # Test on the remaining data:
    E = np.zeros(len(test_data))
    F = []
    for i, test_atoms in enumerate(test_data):
        test_atoms.calc = model
        E[i] = test_atoms.get_potential_energy()
        F += list(test_atoms.get_forces().flatten())
    F = np.array(F)

    if test_mode:
        expected_energies = expected_data["E"]
        np.testing.assert_allclose(E, expected_energies, **tolerance)
        expected_forces = expected_data["F"]

        if force_tolerance is None:
            force_tolerance = tolerance

        np.testing.assert_allclose(F, expected_forces, **force_tolerance)

        # # Model parameters:
        # parameters = model.get_model_parameters()
        # recreated_model = model_maker(*model_args, **model_kwargs)

        # recreated_model.set_model_parameters(parameters)
        # recreated_energies = np.array([recreated_model.predict_energy(atoms) for atoms in test_data])
        # np.testing.assert_allclose(E, recreated_energies)

    return {"E": E, "F": F}
